import os
import argparse
import torch
import torch.nn.functional as F
from torchvision import transforms
from diffusers import DiffusionPipeline, UNet2DConditionModel
from diffusers.loaders import AttnProcsLayers
from diffusers.models.attention_processor import LoRAAttnProcessor
from diffusers.optimization import get_scheduler
from transformers import CLIPTextModel, CLIPTokenizer
from datasets import load_dataset
from tqdm.auto import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tuning LoRA pour Stable Diffusion")
    parser.add_argument("--pretrained_model_name_or_path", type=str, default="runwayml/stable-diffusion-v1-5")
    parser.add_argument("--dataset_dir", type=str, default="./Iwaria_Press_Dataset/images")
    parser.add_argument("--output_dir", type=str, default="./output")
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--train_batch_size", type=int, default=2)
    parser.add_argument("--num_train_epochs", type=int, default=10)
    parser.add_argument("--learning_rate", type=float, default=1e-4)
    parser.add_argument("--adam_weight_decay", type=float, default=1e-2)
    return parser.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # 1. Chargement des composants du modèle de base
    tokenizer = CLIPTokenizer.from_pretrained(args.pretrained_model_name_or_path, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(args.pretrained_model_name_or_path, subfolder="text_encoder")
    unet = UNet2DConditionModel.from_pretrained(args.pretrained_model_name_or_path, subfolder="unet")

    # Geler les paramètres existants du modèle de base
    text_encoder.requires_grad_(False)
    unet.requires_grad_(False)
    
    # 2. Injection des couches LoRA dans l'UNet
    lora_attn_procs = {}
    for name, attn_processor in unet.attn_processors.items():
        cross_attention_dim = None if name.endswith("attn1.processor") else unet.config.cross_attention_dim
        if name.startswith("mid_block"):
            hidden_size = unet.config.block_out_channels[-1]
        elif name.startswith("up_blocks"):
            block_id = int(name.split(".")[1])
            hidden_size = list(reversed(unet.config.block_out_channels))[block_id]
        elif name.startswith("down_blocks"):
            block_id = int(name.split(".")[1])
            hidden_size = unet.config.block_out_channels[block_id]

        lora_attn_procs[name] = LoRAAttnProcessor(
            hidden_size=hidden_size, cross_attention_dim=cross_attention_dim, rank=4
        )
    
    unet.set_attn_processor(lora_attn_procs)
    lora_layers = AttnProcsLayers(unet.attn_processors)
    
    # Passer l'UNet en mode entraînement uniquement pour les couches LoRA
    unet.train()
    
    # 3. Optimiseur & Scheduler
    optimizer = torch.optim.AdamW(
        lora_layers.parameters(),
        lr=args.learning_rate,
        weight_decay=args.adam_weight_decay,
    )
    
    # 4. Préparation du Jeu de Données Local
    # Charge automatiquement les images et lit le fichier metadata.jsonl
    dataset = load_dataset("imagefolder", data_dir=args.dataset_dir, split="train")
    
    # Transformations appliquées aux images (Redimensionnement, Mise au carré, Normalisation)
    train_transforms = transforms.Compose([
        transforms.Resize(args.resolution, interpolation=transforms.InterpolationMode.BILINEAR),
        transforms.CenterCrop(args.resolution),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]),
    ])
    
    def preprocess(examples):
        images = [train_transforms(image.convert("RGB")) for image in examples["image"]]
        inputs = tokenizer(examples["text"], max_length=tokenizer.model_max_length, padding="max_length", truncation=True, return_tensors="pt")
        return {"pixel_values": images, "input_ids": inputs.input_ids}

    train_dataset = dataset.with_transform(preprocess)
    
    def collate_fn(examples):
        pixel_values = torch.stack([example["pixel_values"] for example in examples])
        input_ids = torch.stack([example["input_ids"] for example in examples])
        return {"pixel_values": pixel_values, "input_ids": input_ids}

    train_dataloader = torch.utils.data.DataLoader(
        train_dataset, batch_size=args.train_batch_size, shuffle=True, collate_fn=collate_fn
    )
    
    # Basculer les modèles sur GPU si disponible
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Entraînement en cours sur l'appareil : {device}")
    
    unet.to(device)
    text_encoder.to(device)
    
    
    # 5. Boucle d'entraînement (Bruitage gaussien et prédiction)
    for epoch in range(args.num_train_epochs):
        progress_bar = tqdm(total=len(train_dataloader), desc=f"Epoch {epoch+1}")
        for step, batch in enumerate(train_dataloader):
            # Convertir les images en espace latent (On simule ici l'apprentissage direct)
            # Pour un script de production complet, on passerait par le VAE, simplifié ici pour la clarté.
            pixel_values = batch["pixel_values"].to(device)
            input_ids = batch["input_ids"].to(device)

            # Génération du bruit aléatoire (Gaussian Noise) à ajouter aux images
            noise = torch.randn_like(pixel_values)
            timesteps = torch.randint(0, 1000, (pixel_values.shape[0],), device=device).long()
            
            # Ajout du bruit à l'image selon le timestep (Forward Diffusion Process)
            noisy_images = pixel_values + noise # Version simplifiée du processus de diffusion

            # Extraction des embeddings textuels de vos légendes explicites
            encoder_hidden_states = text_encoder(input_ids)[0]

            # L'UNet tente de prédire le bruit qui a été ajouté à l'image
            noise_pred = unet(noisy_images, timesteps, encoder_hidden_states).sample

            # Calcul de la perte (Erreur quadratique entre le vrai bruit et le bruit prédit)
            loss = F.mse_loss(noise_pred.float(), noise.float(), reduction="mean")

            # Rétropropagation
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            progress_bar.update(1)
            progress_bar.set_postfix({"loss": loss.item()})
            
    # 6. Sauvegarde des poids LoRA appris
    print(f"Sauvegarde du modèle affiné dans {args.output_dir}...")
    unet.save_attn_procs(args.output_dir)
    print("Entraînement terminé avec succès !")
    
if __name__ == "__main__":
    main()