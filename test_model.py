from diffusers import DiffusionPipeline
import torch

# 1. Charger le modèle Stable Diffusion de base
pipe = DiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
pipe.to("cuda")

# 2. Charger vos poids spécifiques entraînés sur les images de presse africaines
pipe.load_lora_weights("./output/pytorch_lora_weights.safetensors")

# 3. Générer une image à partir d'un prompt éditorial
prompt = "Une photo de presse d'un ingénieur réseau travaillant sur des serveurs informatiques à Kribi, style éditorial net"
image = pipe(prompt, num_inference_steps=30).images[0]

# 4. Sauvegarder l'image générée
image.save("resultat_generation.jpg")
print("Image générée sous le nom 'resultat_generation.jpg'")