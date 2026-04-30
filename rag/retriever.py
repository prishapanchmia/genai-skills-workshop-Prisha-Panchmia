from google.cloud import bigquery

client = bigquery.Client()

def retrieve_context(user_query: str, top_k: int = 3) -> str:
    query = f"""
    SELECT base.content
    FROM VECTOR_SEARCH(
      TABLE `alaska_snow.ads_embedded`,
      'ml_generate_embedding_result',
      (
        SELECT ml_generate_embedding_result
        FROM ML.GENERATE_EMBEDDING(
          MODEL `alaska_snow.ADS_Embeddings`,
          (SELECT '{user_query}' AS content)
        )
      ),
      top_k => {top_k}
    )
    """
    rows = client.query(query).result()
    return "\n".join([row.content for row in rows])