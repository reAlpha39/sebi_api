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
            INSERT INTO users (name, no_hp, prodi, take_date, image, result_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''

            values = (
                user_data['name'],
                user_data.get('no_hp'),
                user_data.get('prodi'),
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

            base_query = '''
                SELECT
                    u.id,
                    u.name,
                    u.no_hp,
                    u.prodi,
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

            # Start with base conditions
            if not include_deleted:
                base_query += " AND u.deleted_at IS NULL"

            # Always check results deleted_at
            base_query += " AND (r.deleted_at IS NULL OR r.id IS NULL)"

            count_query = '''
                SELECT COUNT(*) as total
                FROM users u
                LEFT JOIN results r ON u.result_id = r.id
                WHERE 1=1
            '''

            if not include_deleted:
                count_query += " AND u.deleted_at IS NULL"
            count_query += " AND (r.deleted_at IS NULL OR r.id IS NULL)"

            params = []

            # Add search condition
            if search:
                search_condition = " AND (u.name LIKE %s OR (u.no_hp IS NOT NULL AND u.no_hp LIKE %s)) OR (u.prodi IS NOT NULL AND u.prodi LIKE %s)"
                base_query += search_condition
                count_query += search_condition
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])

            # Add date filters
            if from_date:
                date_condition = " AND u.take_date >= %s"
                base_query += date_condition
                count_query += date_condition
                params.append(from_date)

            if to_date:
                date_condition = " AND u.take_date <= %s"
                base_query += date_condition
                count_query += date_condition
                params.append(to_date)

            # Get total count
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()['total']

            # Add pagination
            base_query += " ORDER BY u.created_at DESC LIMIT %s OFFSET %s"
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
            SELECT
                u.id,
                u.name,
                u.no_hp,
                u.prodi,
                u.take_date,
                u.image,
                u.result_id,
                r.title as result_title,
                u.created_at,
                u.updated_at,
                u.deleted_at
            FROM users u
            LEFT JOIN results r ON u.result_id = r.id
            WHERE u.id = %s
            AND (r.deleted_at IS NULL OR r.id IS NULL)
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
            check_query = '''
            SELECT u.id
            FROM users u
            WHERE u.id = %s AND u.deleted_at IS NULL
            '''
            cursor.execute(check_query, (user_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404, detail="User not found or already deleted")

            # If result_id is provided, check if it exists
            if 'result_id' in user_data:
                check_result_query = '''
                SELECT id
                FROM results
                WHERE id = %s AND deleted_at IS NULL
                '''
                cursor.execute(check_result_query, (user_data['result_id'],))
                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Result with ID {user_data['result_id']} does not exist or is deleted"
                    )

            take_date_formatted = user_data['take_date'].strftime(
                '%Y-%m-%d %H:%M:%S') if user_data.get('take_date') else None

            update_parts = []
            values = []

            # Dynamically build update query based on provided fields
            if 'name' in user_data:
                update_parts.append("name = %s")
                values.append(user_data['name'])

            if 'no_hp' in user_data:
                update_parts.append("no_hp = %s")
                values.append(user_data.get('no_hp'))

            if 'prodi' in user_data:
                update_parts.append("prodi = %s")
                values.append(user_data.get('prodi'))

            if 'take_date' in user_data:
                update_parts.append("take_date = %s")
                values.append(take_date_formatted)

            if 'image' in user_data:
                update_parts.append("image = %s")
                values.append(user_data['image'])

            if 'result_id' in user_data:
                update_parts.append("result_id = %s")
                values.append(user_data['result_id'])

            # Add updated_at
            update_parts.append("updated_at = %s")
            values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            # Add user_id for WHERE clause
            values.append(user_id)

            update_query = f'''
            UPDATE users 
            SET {', '.join(update_parts)}
            WHERE id = %s AND deleted_at IS NULL
            '''

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
