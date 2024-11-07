from datetime import datetime
from database import get_db_connection
from fastapi import HTTPException
from mysql.connector import Error


class UserModel:
    @staticmethod
    async def create_user(user_data: dict):
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            take_date_formatted = user_data['take_date'].strftime(
                '%Y-%m-%d %H:%M:%S') if user_data.get('take_date') else None

            insert_query = '''
            INSERT INTO users (name, no_hp, take_date, image, result_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''

            values = (
                user_data['name'],
                user_data.get('no_hp'),
                take_date_formatted,
                user_data['image'],
                user_data.get('result_id'),
                current_time,
                current_time
            )

            # Validate result_id exists if provided
            if user_data.get('result_id'):
                check_result_query = "SELECT id FROM results WHERE id = %s"
                cursor.execute(check_result_query, (user_data['result_id'],))
                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Result with ID {user_data['result_id']} does not exist"
                    )

            cursor.execute(insert_query, values)
            user_id = cursor.lastrowid
            db.commit()

            # Fetch the created user
            return await UserModel.get_user_by_id(user_id)

        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @staticmethod
    async def get_users(page: int, limit: int, include_deleted: bool, search: str = None,
                        from_date: datetime = None, to_date: datetime = None):
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            Copybase_query = '''
                SELECT
                    u.id,
                    u.name,
                    u.no_hp,
                    u.take_date,
                    u.image,
                    u.result_id,
                    r.title as result_title,
                    u.created_at,
                    u.updated_at,
                    u.deleted_at
                FROM users u
                LEFT JOIN results r ON u.result_id = r.id
                WHERE 1=1
            '''

            count_query = "SELECT COUNT(*) as total FROM users WHERE 1=1"
            params = []

            # Add search condition
            if search:
                search_condition = " AND (name LIKE %s OR (no_hp IS NOT NULL AND no_hp LIKE %s))"
                base_query += search_condition
                count_query += search_condition
                search_param = f"%{search}%"
                params.extend([search_param, search_param])

            # Add date filters
            if from_date:
                date_condition = " AND take_date >= %s"
                base_query += date_condition
                count_query += date_condition
                params.append(from_date)

            if to_date:
                date_condition = " AND take_date <= %s"
                base_query += date_condition
                count_query += date_condition
                params.append(to_date)

            if not include_deleted:
                deleted_condition = " AND deleted_at IS NULL"
                base_query += deleted_condition
                count_query += deleted_condition

            # Get total count
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()['total']

            # Add pagination
            base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * limit
            params.extend([limit, offset])

            cursor.execute(base_query, params)
            users = cursor.fetchall()

            return users, total_records

        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @staticmethod
    async def get_user_by_id(user_id: int):
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            select_query = '''
            SELECT id, name, no_hp, take_date, image, created_at, updated_at, deleted_at
            FROM users 
            WHERE id = %s
            '''

            cursor.execute(select_query, (user_id,))
            user = cursor.fetchone()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            return user

        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @staticmethod
    async def update_user(user_id: int, user_data: dict):
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            # Check if user exists and is not deleted
            check_query = "SELECT id FROM users WHERE id = %s AND deleted_at IS NULL"
            cursor.execute(check_query, (user_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404, detail="User not found or already deleted")

            take_date_formatted = user_data['take_date'].strftime(
                '%Y-%m-%d %H:%M:%S') if user_data.get('take_date') else None

            update_query = '''
            UPDATE users 
            SET name = %s, no_hp = %s, take_date = %s, image = %s
            WHERE id = %s AND deleted_at IS NULL
            '''

            values = (
                user_data['name'],
                user_data.get('no_hp'),
                take_date_formatted,
                user_data['image'],
                user_id
            )

            cursor.execute(update_query, values)
            db.commit()

            return await UserModel.get_user_by_id(user_id)

        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @staticmethod
    async def delete_user(user_id: int):
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            update_query = '''
            UPDATE users 
            SET deleted_at = %s 
            WHERE id = %s AND deleted_at IS NULL
            '''

            cursor.execute(update_query, (current_time, user_id))
            db.commit()

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404, detail="User not found or already deleted")

            return {"status": "success", "message": f"User {user_id} successfully deleted"}

        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()
