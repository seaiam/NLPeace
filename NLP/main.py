import data_processing as dp
import models
from logger_config import configure_logger
logger = configure_logger(__name__)


logger.info("Starting the NLP pipeline...")
df = dp.import_data()
df = dp.process_data(df)
X, y = models.vectorize_data(df)
models.train_random_forest(X, y)
models.train_xgboost(X, y)
