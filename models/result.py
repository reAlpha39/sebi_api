from datetime import datetime
from database import get_db_connection
from fastapi import HTTPException
from mysql.connector import Error


class ResultModel:
    @staticmethod
    async def create_result(result_data: dict):
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            insert_query = '''
            INSERT INTO results (title, description, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            '''

            values = (
                result_data['title'],
                result_data.get('description'),
                current_time,
                current_time
            )

            cursor.execute(insert_query, values)
            result_id = cursor.lastrowid
            db.commit()

            # Fetch the created result
            return await ResultModel.get_result_by_id(result_id)

        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @staticmethod
    async def get_result_by_id(result_id: int):
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            select_query = '''
            SELECT id, title, description, created_at, updated_at
            FROM results
            WHERE id = %s
            '''

            cursor.execute(select_query, (result_id,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Result not found")

            return result

        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @staticmethod
    async def get_all_results():
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            select_query = '''
            SELECT id, title, description, created_at, updated_at
            FROM results
            ORDER BY created_at DESC
            '''

            cursor.execute(select_query)
            results = cursor.fetchall()

            return results

        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()
