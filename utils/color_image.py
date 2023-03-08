from PIL import Image
import os 

def apply_color(image_path, color_hex:str,alpha=0.5):
    color_hex = color_hex.lstrip('#')
    # Open the input image
    img = Image.open(image_path)
    
    # Convert the input image to RGBA
    img = img.convert("RGBA")
    
    # Get the RGBA values of the input color
    color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    
    # Create a new image with the same size and mode as the input image
    new_img = Image.new("RGBA", img.size, color)
    
    # Blend the input image and the new image using the "over" blending mode
    blended_img = Image.blend(new_img, img, alpha=alpha)
    
    out_path = f"{os.path.splitext(os.path.basename(image_path))[0]}_{color_hex}.png"
    # Save the blended image
    blended_img.save(out_path)
    return out_path
    
# Example usage
if __name__=="__main__":
    apply_color("./utils/stainless steel_2.png", "#FF0000",alpha=0.5)