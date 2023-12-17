import unittest
import os
from unittest.mock import patch, MagicMock
from WilmaTask import connect_mongodb, add_unique_item_mongodb, find_items_mongodb, delete_from_mongodb
from datetime import datetime
from mongodbconnectiontest import create_mongodb_connection
from dotenv import load_dotenv

# Testaa MongoDB:n yhteyttä ja funktiot

class TestMongoDBOperations(unittest.TestCase):
    
    def test_mongodb_connection_success(self):
        load_dotenv()
        uri = os.environ["ATLAS_URI"]
        # This will test the actual connection to MongoDB
        connection_successful = create_mongodb_connection(uri)
        self.assertTrue(connection_successful, False)

    @patch('WilmaTask.MongoClient')
    def test_connect_mongodb(self, mock_client):
        # Set up the mock
        mock_collection = MagicMock()
        mock_client.return_value.__getitem__.return_value.__getitem__.return_value = mock_collection

        # Call the function
        result = connect_mongodb('test_collection')

        # Assert the result is the mock collection
        self.assertEqual(result, mock_collection)

    @patch('WilmaTask.MongoClient')
    def test_add_unique_item_mongodb(self, mock_client):
        # Mock setup
        mock_db = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_db.find_one.return_value = None

        # Call the function
        add_unique_item_mongodb('subject', 'description', datetime.now(), datetime.now(), mock_db)

        # Assert that insert_one was called
        mock_db.insert_one.assert_called_once()

    @patch('WilmaTask.MongoClient')
    def test_find_items_mongodb(self, mock_client):
        # Mock setup
        mock_collection = MagicMock()
        mock_client.return_value.__getitem__.return_value.__getitem__.return_value = mock_collection

        # Call the function
        find_items_mongodb(mock_collection)

        # Assert that find was called
        mock_collection.find.assert_called_once()

    @patch('WilmaTask.MongoClient')
    def test_delete_from_mongodb(self, mock_client):
        # Mock setup
        mock_collection = MagicMock()
        mock_client.return_value.__getitem__.return_value.__getitem__.return_value = mock_collection

        # Call the function
        delete_from_mongodb(mock_collection)

        # Assert that delete_many was called
        mock_collection.delete_many.assert_called_once()


