"""
MongoDB Atlas connection and initialization.
Handles async MongoDB connection using Motor and Beanie.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.db.models import User, Session, Message, Document
from app import config

logger = logging.getLogger(__name__)

# Global database instance
db: AsyncIOMotorDatabase = None
client: AsyncIOMotorClient = None


async def connect_db() -> None:
    """
    Initialize MongoDB connection and Beanie.
    Called on application startup.
    """
    global db, client

    try:
        if not config.MONGODB_URI:
            raise ValueError("MONGODB_URI environment variable not set")

        logger.info("Connecting to MongoDB Atlas...")

        # Create async MongoDB client
        # logger.warning("Using MongoDB URI: %s", config.MONGODB_URI)  # Log the URI for debugging (be cautious with sensitive info)
        client = AsyncIOMotorClient(config.MONGODB_URI)

        # Test connection by pinging
        await client.admin.command("ping")
        logger.info("✓ Successfully connected to MongoDB Atlas")

        # Get database reference
        db = client[config.DATABASE_NAME]

        # Initialize Beanie ORM with models
        await init_beanie(
            database=db,
            document_models=[User, Session, Message, Document]
        )

        logger.info("✓ Beanie initialized with models")

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_db() -> None:
    """
    Close MongoDB connection.
    Called on application shutdown.
    """
    global client

    if client:
        try:
            client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")


def get_db() -> AsyncIOMotorDatabase:
    """
    Get the current database instance.
    For dependency injection in routes.
    
    Returns:
        AsyncIOMotorDatabase instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return db
