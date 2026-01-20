#!/usr/bin/env python3
"""
Test script to validate biometric model accuracy using test images.
Uses DeepFace with ArcFace/Facenet for facial recognition.
"""

import os
import sys
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test DeepFace availability
print("=" * 60)
print("BIOMETRIC MODEL TEST SCRIPT")
print("=" * 60)

try:
    from deepface import DeepFace
    from scipy.spatial.distance import cosine
    print("✅ DeepFace loaded successfully!")
    DEEPFACE_AVAILABLE = True
except ImportError as e:
    print(f"❌ DeepFace import failed: {e}")
    DEEPFACE_AVAILABLE = False

# Image paths
IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')
TEST_IMAGES = {
    'Ajith': ['Ajith1.jpg', 'Ajith2.jpg'],
    'Vijay': ['Vijay1.jpeg', 'Vijay2.jpg'],
    'Simran': ['Simran1.jpg'],
}

def extract_embedding(image_path, model_name='Facenet512'):
    """Extract face embedding using DeepFace."""
    try:
        result = DeepFace.represent(
            img_path=image_path,
            model_name=model_name,
            enforce_detection=True,
            detector_backend='retinaface'
        )
        if result and len(result) > 0:
            embedding = np.array(result[0]['embedding'], dtype=np.float32)
            # L2 normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            return embedding
        return None
    except Exception as e:
        print(f"  ⚠ Error extracting from {os.path.basename(image_path)}: {e}")
        return None

def compute_similarity(emb1, emb2):
    """Compute cosine similarity between two embeddings."""
    if emb1 is None or emb2 is None:
        return 0.0
    # Cosine distance -> similarity
    distance = cosine(emb1, emb2)
    similarity = 1.0 - distance
    return float(similarity)

def run_tests():
    if not DEEPFACE_AVAILABLE:
        print("❌ Cannot run tests - DeepFace not available")
        return
    
    print("\n" + "=" * 60)
    print("TESTING FACE RECOGNITION MODEL")
    print("=" * 60)
    
    # Try different models
    models = ['Facenet512', 'ArcFace', 'Facenet']
    
    for model_name in models:
        print(f"\n>>> Testing with model: {model_name}")
        print("-" * 40)
        
        embeddings = {}
        
        # Extract embeddings for all images
        for person, images in TEST_IMAGES.items():
            embeddings[person] = []
            for img in images:
                img_path = os.path.join(IMAGES_DIR, img)
                if os.path.exists(img_path):
                    print(f"  Extracting: {img}...", end=" ")
                    emb = extract_embedding(img_path, model_name)
                    if emb is not None:
                        embeddings[person].append((img, emb))
                        print(f"✅ ({len(emb)}D)")
                    else:
                        print("❌ Failed")
                else:
                    print(f"  ⚠ {img} not found")
        
        # Test same-person verification (should be HIGH similarity)
        print(f"\n  📊 SAME PERSON TESTS (should be >= 0.65):")
        for person, emb_list in embeddings.items():
            if len(emb_list) >= 2:
                img1, emb1 = emb_list[0]
                img2, emb2 = emb_list[1]
                sim = compute_similarity(emb1, emb2)
                status = "✅" if sim >= 0.65 else "❌"
                print(f"     {person}: {img1} vs {img2} = {sim:.4f} ({sim*100:.2f}%) {status}")
        
        # Test different-person verification (should be LOW similarity)
        print(f"\n  📊 DIFFERENT PERSON TESTS (should be < 0.65):")
        persons = list(embeddings.keys())
        for i in range(len(persons)):
            for j in range(i+1, len(persons)):
                p1, p2 = persons[i], persons[j]
                if embeddings[p1] and embeddings[p2]:
                    img1, emb1 = embeddings[p1][0]
                    img2, emb2 = embeddings[p2][0]
                    sim = compute_similarity(emb1, emb2)
                    status = "✅" if sim < 0.65 else "❌ (FALSE POSITIVE)"
                    print(f"     {p1} vs {p2}: {img1} vs {img2} = {sim:.4f} ({sim*100:.2f}%) {status}")
        
        print()
        break  # Only test first successful model

if __name__ == '__main__':
    run_tests()
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
