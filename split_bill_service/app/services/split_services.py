from app.core.config import settings
import logging
from typing import Dict

logger = logging.getLogger(__name__)


async def split_by_dishes(dishes: Dict[str, Dict[str, float]], 
                          prices: Dict[str, float],  
                          discount: float, 
                          tax: float, 
                          tip: float, 
                          service_fee: float) -> Dict[str, float]:
    """
    Chia tiền bill dựa trên các món ăn mà mỗi người đã dùng.
    Áp dụng discount, thuế, tip và phí dịch vụ cho từng món trước khi chia cho mỗi người.
    
    Args:
        dishes (dict): Dictionary với key là tên món, value là dict ánh xạ từ tên người đến phần ăn
                      Ví dụ: {'Món A': {'Alice': 1, 'Bob': 0.5, 'Charlie': 0.5}, 'Món B': {'Alice': 0, 'Bob': 1, 'Charlie': 0}}
        prices (dict): Dictionary với key là tên món, value là giá tiền mỗi món
                      Ví dụ: {'Món A': 100000, 'Món B': 80000}
        discount (float, optional): % giảm giá (0.1 = 10%). Defaults to 0.
        tax (float, optional): % thuế (0.08 = 8%). Defaults to 0.
        tip (float, optional): % tiền tip (0.15 = 15%). Defaults to 0.
        service_fee (float, optional): % phí dịch vụ khác (0.05 = 5%). Defaults to 0.
    
    Returns:
        dict: Dictionary với key là tên người, value là số tiền phải trả
    """
    # Tìm tất cả người tham gia
    all_people = set()
    for dish_users in dishes.values():
        all_people.update(dish_users.keys())
    
    # Khởi tạo dict lưu trữ số tiền mỗi người phải trả
    individual_costs = {person: 0 for person in all_people}
    
    # Hệ số điều chỉnh cho discount, thuế, tip và phí dịch vụ
    adjustment_factor = (1 - discount + tax + tip + service_fee)
    
    # Tính tiền món ăn cho từng người
    for dish_name, dish_users in dishes.items():
        # Giá gốc món ăn
        dish_price = prices[dish_name]
        
        # Áp dụng discount, thuế, tip và phí dịch vụ cho món ăn
        adjusted_dish_price = dish_price * adjustment_factor
        
        # Tính tổng phần ăn để chia đều giá tiền
        total_portions = sum(dish_users.values())
        
        if total_portions == 0:
            continue
        
        # Tính giá tiền cho mỗi phần đã điều chỉnh các khoản phí
        price_per_portion = adjusted_dish_price / total_portions
        
        # Tính tiền mỗi người phải trả cho món này
        for person, portion in dish_users.items():
            individual_costs[person] += price_per_portion * portion
    
    # Làm tròn số tiền của mỗi người
    for person in individual_costs:
        individual_costs[person] = round(individual_costs[person], 2)
    
    return individual_costs

async def split_equal_by_names(
    total_amount: float, 
    people_names: list) -> Dict[str, float]:
    """
    Chia đều tổng số tiền cho danh sách người được cung cấp.
    
    Args:
        total_amount (float): Tổng số  tiền cần chia
        people_names (list): Danh sách tên những người tham gia
    
    Returns:
        dict: Dictionary với key là tên người, value là số tiền phải trả
    """
    
    num_people = len(people_names)
    amount_per_person = total_amount / num_people
    
    # Tạo dictionary kết quả
    result = {person: round(amount_per_person, 2) for person in people_names}
    
    # Đảm bảo tổng các khoản sau khi làm tròn bằng đúng với tổng ban đầu
    total_after_rounding = sum(result.values())
    
    # Nếu có sai số do làm tròn, điều chỉnh cho người đầu tiên trong danh sách
    if abs(total_after_rounding - total_amount) >= 0.01:
        adjustment = total_amount - total_after_rounding
        first_person = people_names[0]
        result[first_person] = round(result[first_person] + adjustment, 2)
    
    return result

async def split_by_percent(total_amount: float,
                           percentages: dict) -> Dict[str, float]:
    """
    Chia tổng số tiền theo tỷ lệ phần trăm cho mỗi người.
    
    Args:
        total_amount (float): Tổng số tiền cần chia
        percentages (dict): Dictionary với key là tên người, value là tỷ lệ phần trăm đóng góp
                           Ví dụ: {'Alice': 30, 'Bob': 40, 'Charlie': 30}
    
    Returns:
        dict: Dictionary với key là tên người, value là số tiền phải trả
    """
    
    # Kiểm tra tổng tỷ lệ phần trăm
    total_percent = sum(percentages.values())
    if abs(total_percent - 100) > 0.001:
        raise ValueError(f"Invalid percent: Sum of percent must be 100%")
    
    # Tính toán số tiền cho mỗi người
    result = {}
    for person, percent in percentages.items():
        amount = total_amount * (percent / 100)
        result[person] = round(amount, 2)
    
    # Kiểm tra và điều chỉnh sai số làm tròn
    total_after_rounding = sum(result.values())
    if abs(total_after_rounding - total_amount) >= 0.01:
        # Tìm người có phần trăm cao nhất để điều chỉnh
        max_percent_person = max(percentages, key=percentages.get)
        adjustment = total_amount - total_after_rounding
        result[max_percent_person] = round(result[max_percent_person] + adjustment, 2)
    
    return result