import numpy as np
from sqlalchemy import text
from app.db.database import engine

def _vec_literal(embedding: np.ndarray) -> str:
    return "[" + ",".join(map(str, embedding.tolist())) + "]"

class PgVectorStore:
    async def add_message(self, session_id: str, role: str, content: str, embedding: np.ndarray | None):
        async with engine.begin() as conn:
            if embedding is not None:
                vec_literal = _vec_literal(embedding)
                sql = f"""
                    INSERT INTO chat_messages (session_id, role, content, embedding)
                    VALUES ('{session_id}', '{role}', '{content.replace("'", "''")}', '{vec_literal}'::vector)
                """
            else:
                sql = f"""
                    INSERT INTO chat_messages (session_id, role, content)
                    VALUES ('{session_id}', '{role}', '{content.replace("'", "''")}')
                """

            await conn.exec_driver_sql(sql)

    async def search_similar(
            self,
            vec,
            limit: int = 5,
            threshold: float | None = None,
            session_filter: str | None = None
        ):
        vec_literal = "[" + ",".join(map(str, vec.tolist())) + "]"

        # Build WHERE clause
        where_clause = ""
        if session_filter:
            where_clause = f"WHERE session_id = '{session_filter}'"

        if threshold is not None:
            where_clause += (" AND " if where_clause else "WHERE ") + \
                            f"1 - (embedding <=> '{vec_literal}'::vector) >= {threshold}"

        sql = f"""
            SELECT id, session_id, role, content,
                   1 - (embedding <=> '{vec_literal}'::vector) AS similarity
            FROM chat_messages
            {where_clause}
            ORDER BY similarity DESC
            LIMIT {limit};
        """

        async with engine.begin() as conn:
            result = await conn.exec_driver_sql(sql)
            rows = result.mappings().all()  # returns list of dict-like RowMapping objects
            return rows

