import pytesseract
import cv2
import numpy as np
import io
import re
from PIL import Image
from fastapi import UploadFile
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure pytesseract path
pytesseract.pytesseract.tesseract_cmd = settings.PYTESSERACT_PATH

async def extract_text_from_image(image: UploadFile) -> str:
    """
    Extract text from an image using pytesseract
    """
    try:
        # Read the image file
        contents = await image.read()
        image_array = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Preprocess the image
        img = preprocess_image(img)
        
        # Extract text using pytesseract with Russian language
        text = pytesseract.image_to_string(img, lang='rus')
        
        logger.debug(f"Extracted text: {text}")
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise

def preprocess_image(img):
    """
    Preprocess the image to improve OCR accuracy
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    # Noise removal
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    return opening

def parse_receipt_data(text: str) -> Dict[str, Any]:
    """
    Parse the extracted text to get receipt information
    """
    result = {
        "is_receipt": False,
        "bill_date": None,
        "tax_amount": 0.00,
        "discount_amount": 0.00,
        "total_amount": 0.00,
        "items": []
    }
    
    # Check if it's a valid receipt by looking for key elements
    if not text or len(text) < 10:
        return result
    
    lines = text.split('\n')
    clean_lines = [line.strip() for line in lines if line.strip()]
    
    # Extract date
    date_pattern = r'(\d{2}[./-]\d{2}[./-]\d{4})'
    date_matches = re.findall(date_pattern, text)
    if date_matches:
        # Convert date to YYYY-MM-DD format
        try:
            date_str = date_matches[0]
            # Handle different date formats (DD.MM.YYYY, DD/MM/YYYY)
            if '.' in date_str:
                day, month, year = date_str.split('.')
            elif '/' in date_str:
                day, month, year = date_str.split('/')
            elif '-' in date_str:
                day, month, year = date_str.split('-')
            
            result["bill_date"] = f"{year}-{month}-{day}"
        except Exception as e:
            logger.error(f"Error parsing date: {str(e)}")
    
    # Extract total amount
    total_patterns = [
        r'Всего:?\s*(\d+[.,]\d+)',
        r'Итого к оплате:?\s*(\d+[.,]\d+)',
        r'К оплате:?\s*(\d+[.,]\d+)',
        r'ИТОГО:?\s*(\d+[.,]\d+)'
    ]
    
    for pattern in total_patterns:
        total_matches = re.findall(pattern, text, re.IGNORECASE)
        if total_matches:
            try:
                total_amount = float(total_matches[0].replace(',', '.'))
                result["total_amount"] = total_amount
                break
            except ValueError:
                continue
    
    # Extract tax amount if available
    tax_patterns = [
        r'НДС:?\s*(\d+[.,]\d+)',
        r'VAT:?\s*(\d+[.,]\d+)'
    ]
    
    for pattern in tax_patterns:
        tax_matches = re.findall(pattern, text, re.IGNORECASE)
        if tax_matches:
            try:
                tax_amount = float(tax_matches[0].replace(',', '.'))
                result["tax_amount"] = tax_amount
                break
            except ValueError:
                continue
    
    # Extract discount amount if available
    discount_patterns = [
        r'Скидка:?\s*(\d+[.,]\d+)',
        r'Discount:?\s*(\d+[.,]\d+)'
    ]
    
    for pattern in discount_patterns:
        discount_matches = re.findall(pattern, text, re.IGNORECASE)
        if discount_matches:
            try:
                discount_amount = float(discount_matches[0].replace(',', '.'))
                result["discount_amount"] = discount_amount
                break
            except ValueError:
                continue
    
    # Extract items
    current_item = None
    items = []
    
    # Regular expression patterns for item extraction
    item_pattern = r'([А-Яа-яA-Za-z\s\./\-]+)\s+(\d+[.,]?\d*)\s+(\d+[.,]?\d*)'
    price_pattern = r'(\d+[.,]\d+)'
    
    # Extract items from receipt text
    for i, line in enumerate(clean_lines):
        # Skip header lines
        if i < 5:
            continue
        
        # Try to match item pattern
        item_matches = re.search(item_pattern, line)
        if item_matches:
            item_name = item_matches.group(1).strip()
            try:
                quantity = float(item_matches.group(2).replace(',', '.'))
                total_price = float(item_matches.group(3).replace(',', '.'))
                unit_price = total_price / quantity if quantity else 0
                
                items.append({
                    "description": item_name,
                    "quantity": quantity,
                    "unit_price": round(unit_price, 2),
                    "total_price": total_price
                })
            except (ValueError, ZeroDivisionError):
                continue
        
        # Alternative approach: Look for lines with price pattern and check previous lines for item name
        elif re.search(price_pattern, line) and i > 0:
            price_matches = re.findall(price_pattern, line)
            if len(price_matches) >= 2:
                try:
                    # If we find at least two prices, assume they are unit price and total price
                    unit_price = float(price_matches[0].replace(',', '.'))
                    total_price = float(price_matches[1].replace(',', '.'))
                    
                    # Estimate quantity based on unit and total price
                    quantity = round(total_price / unit_price, 2) if unit_price else 1
                    
                    # Check previous line for potential item name
                    prev_line = clean_lines[i-1].strip()
                    if not re.search(price_pattern, prev_line):
                        items.append({
                            "description": prev_line,
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "total_price": total_price
                        })
                except (ValueError, ZeroDivisionError, IndexError):
                    continue
    
    # Special case: Try to extract items using column-based approach
    # This works when receipt items are organized in columns
    if not items:
        # Look for patterns where items, quantities, and prices are in separate columns
        for i in range(len(clean_lines) - 2):
            line = clean_lines[i]
            if not re.search(price_pattern, line):
                # This might be an item description
                next_line = clean_lines[i+1]
                # Check if next line contains numbers that could be quantity/price
                if re.search(r'\d+[.,]?\d*', next_line):
                    try:
                        numbers = re.findall(r'\d+[.,]?\d*', next_line)
                        if len(numbers) >= 2:
                            quantity = float(numbers[0].replace(',', '.'))
                            total_price = float(numbers[-1].replace(',', '.'))
                            unit_price = total_price / quantity if quantity else 0
                            
                            items.append({
                                "description": line.strip(),
                                "quantity": quantity,
                                "unit_price": round(unit_price, 2),
                                "total_price": total_price
                            })
                    except (ValueError, ZeroDivisionError):
                        continue
    
    # Second approach - try to find items by finding price column position and working backwards
    if not items:
        # Find the position of price columns
        price_positions = []
        for line in clean_lines:
            price_matches = re.finditer(r'\d+[.,]\d+', line)
            for match in price_matches:
                price_positions.append(match.start())
        
        # If we have consistent price positions, use them to extract items
        if price_positions:
            avg_price_pos = sum(price_positions) // len(price_positions)
            
            for line in clean_lines:
                if len(line) > avg_price_pos:
                    # Split line at average price position
                    item_part = line[:avg_price_pos].strip()
                    price_part = line[avg_price_pos:].strip()
                    
                    if item_part and price_part:
                        price_matches = re.findall(price_pattern, price_part)
                        if price_matches:
                            try:
                                total_price = float(price_matches[0].replace(',', '.'))
                                # Default quantity to 1 if not specified
                                quantity = 1.0
                                
                                # Try to extract quantity from item part
                                qty_match = re.search(r'(\d+[.,]?\d*)\s*[xхХ]', item_part)
                                if qty_match:
                                    quantity = float(qty_match.group(1).replace(',', '.'))
                                    # Remove quantity from item description
                                    item_part = re.sub(r'\d+[.,]?\d*\s*[xхХ]', '', item_part).strip()
                                
                                unit_price = total_price / quantity
                                
                                items.append({
                                    "description": item_part,
                                    "quantity": quantity,
                                    "unit_price": round(unit_price, 2),
                                    "total_price": total_price
                                })
                            except (ValueError, ZeroDivisionError):
                                continue
    
    # If we found items and at least one has a positive price and quantity,
    # or total amount is positive, mark as a valid receipt
    if items and any(item["quantity"] > 0 and item["total_price"] > 0 for item in items):
        result["is_receipt"] = True
    elif result["total_amount"] > 0:
        result["is_receipt"] = True
    
    result["items"] = items
    return result