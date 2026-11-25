import logging
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.rag_service import ingest_documents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("phishguard.rag_ingest")


def main() -> int:
    logger.info("Starting cybersecurity knowledge base ingestion...")

    try:
        result = ingest_documents()
        logger.info(
            "Ingestion completed successfully: %d documents, %d chunks -> %s",
            result["documents"],
            result["chunks"],
            result["index_path"],
        )
        print(f"\nSUCCESS: Ingested {result['documents']} documents into {result['chunks']} chunks.")
        print(f"Index location: {result['index_path']}")
        return 0

    except Exception as exc:
        logger.exception("Ingestion failed: %s", exc)
        print(f"\nERROR: Failed to ingest documents: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
