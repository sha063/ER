from pdf2image import convert_from_path
import os
import pytesseract
from PIL import Image


def convert_to_images_and_ocr(file_path, output_dir, dpi=300, lang="eng"):
    """
    Converts a PDF or image file to images, performs OCR on each image,
    and saves the text to a single file.

    Parameters:
    - file_path (str): Path to the PDF or image file.
    - output_dir (str): Directory to save the output images and text file.
    - dpi (int): Resolution in dots per inch for PDF conversion (default: 300).
    - lang (str): Language for OCR (default: 'eng').
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Path to save the extracted text
        text_file_path = os.path.join(output_dir, "extracted_text.txt")

        if file_path.lower().endswith(".pdf"):
            # Convert PDF to images
            images = convert_from_path(file_path, dpi=dpi)
        elif file_path.lower().endswith(
            (".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp")
        ):
            # Load single image
            images = [Image.open(file_path)]
        else:
            raise ValueError(
                "Unsupported file type. Supported types are PDF, JPG, JPEG, PNG, GIF, TIFF, and BMP."
            )

        with open(text_file_path, "w", encoding="utf-8") as text_file:
            # Process each image
            for i, image in enumerate(images):
                if len(images) > 1:
                    image_path = os.path.join(output_dir, f"page_{i + 1}.jpg")
                    image.save(image_path, "JPEG")
                    print(f"Saved {image_path}")

                # Perform OCR on the image
                custom_config = r"--oem 3 --psm 1"  # Set Tesseract to use the LSTM OCR engine and automatic page segmentation
                text = pytesseract.image_to_string(
                    image, lang=lang, config=custom_config
                )

                text_file.write(f"--- Page {i + 1} ---\n")
                text_file.write(text)
                text_file.write("\n\n")

                if len(images) > 1:
                    # Delete the image after OCR if it was converted from a PDF
                    os.remove(image_path)
                    print(f"Deleted {image_path}")

        print(f"OCR completed, and text saved to {text_file_path}.")
        return True

    except Exception as e:
        print(f"Error processing file: {e}")
        return False


# Example usage
if __name__ == "__main__":
    file_to_convert = "a.pdf"  # Replace with your file path (PDF or image)
    output_directory = "output"  # Replace with your output directory
    convert_to_images_and_ocr(file_to_convert, output_directory)
