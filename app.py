# -------------------------------------------
# 📦 Imports
# -------------------------------------------
from flask import render_template, Flask, request, Response
from prometheus_client import Counter, generate_latest  # For Prometheus metrics
from rag_pipeline.data_ingestion import (
    DataIngestor,
)  # Custom module to ingest vector store
from rag_pipeline.rag_chain import RAGChainBuilder  # Custom RAG chain builder

from dotenv import load_dotenv  # Load environment variables from .env file

load_dotenv()

# -------------------------------------------
# 📈 Prometheus Metric: Count total HTTP requests
# -------------------------------------------
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Request")


# -------------------------------------------
# 🚀 Flask App  Function
# -------------------------------------------
def create_app():
    app = Flask(__name__)  # Initialize Flask app

    # Load vector store (either from disk or freshly generated)
    vector_store = DataIngestor().ingest(load_existing=True)

    # Build the RAG pipeline using the vector store
    rag_chain = RAGChainBuilder(vector_store).build_chain()

    # ---------------------------------------
    # 🏠 Home Route - Renders UI template
    # ---------------------------------------
    @app.route("/")
    def index():
        REQUEST_COUNT.inc()  # Increment Prometheus counter
        return render_template("index.html")

    # ---------------------------------------
    # 💬 Chatbot Response Route
    # ---------------------------------------
    @app.route("/get", methods=["POST"])
    def get_response():
        user_input = request.form["msg"]  # Get user message from form

        # Invoke the RAG chain and retrieve the response
        reponse = rag_chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "user-session"}},
        )["answer"]

        return reponse

    # ---------------------------------------
    # 📊 Prometheus Metrics Endpoint
    # ---------------------------------------
    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype="text/plain")

    return app


# -------------------------------------------
# 🚦 Run the Flask App
# -------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
