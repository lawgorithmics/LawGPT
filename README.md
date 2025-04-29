# Indonesian Law GPT
Simple AI-based application to help Indonesians know more about their ongoing case, what constitutional law is affected, etc.

## How to Run
1. Install necessary packages `pip install -r requirements.txt`
2. Turn on Docker service and Run Posgres VectorDB:
    ```shell
    docker run -d \
            -e POSTGRES_DB=ai \
            -e POSTGRES_USER=ai \
            -e POSTGRES_PASSWORD=ai \
            -e PGDATA=/var/lib/postgresql/data/pgdata \
            -v pgvolume:/var/lib/postgresql/data \
            -p 5532:5432 \
            --name pgvector \
            agnohq/pgvector:16
    ```
3. From root, run `streamlit run src/app.py`. If successful, this will open your browser, `localhost:8501`
4. Wait until everything loads. When it finishes, a text input box appears.
5. Input with your 