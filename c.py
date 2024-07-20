import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
image = cv2.imread('sample.jpg')

# Apply Median Filtering
denoised_image = cv2.medianBlur(image, 5)

# Display the original and denoised images
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title('Original Image')
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

plt.subplot(1, 2, 2)
plt.title('Denoised Image')
plt.imshow(cv2.cvtColor(denoised_image, cv2.COLOR_BGR2RGB))

plt.show()
