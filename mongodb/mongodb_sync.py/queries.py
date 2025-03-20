# queries.py 파일 생성
RESTAURANT_QUERY = """
SELECT 
    r.id as restaurant_id,
    r.name,
    r.address,
    r.average_price,
    r.caution,
    r.convenience,
    r.expanded_days,
    r.is_deleted,
    r.operating_hour,
    r.phone_number,
    r.rating as score,
    r.review_count as review,
    r.time_range as duration_hours,
    rc.category_id
FROM restaurant r
JOIN restaurant_category rc ON r.id = rc.restaurant_id
WHERE r.is_deleted = 0
"""

USER_QUERY = """
SELECT 
    id as user_id,
    sex,
    status,
    is_deleted,
    empty_ticket_count,
    normal_ticket_count
FROM user
WHERE status = 'ACTIVE' AND is_deleted = 0
"""

# 나머지 쿼리들도 추가...

# 파라미터가 있는 쿼리 함수
def get_user_reservations_query(user_id):
    """특정 사용자의 예약 데이터를 가져오는 쿼리"""
    return f"""
    SELECT 
        user_id,
        restaurant_id,
        status,
        reservation_time_id,
        reservation_date,
        seat_type_id
    FROM reservation
    WHERE user_id = {user_id}
    AND status = 'COMPLETED'
    """

def get_reservations_by_date_range_query(start_date, end_date):
    """특정 날짜 범위의 예약 데이터를 가져오는 쿼리"""
    return f"""
    SELECT 
        user_id,
        restaurant_id,
        status,
        reservation_time_id,
        reservation_date,
        seat_type_id
    FROM reservation
    WHERE reservation_date BETWEEN '{start_date}' AND '{end_date}'
    AND status = 'COMPLETED'
    """