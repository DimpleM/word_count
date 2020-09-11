from app import app
import unittest2 

class WordCountTest(unittest2.TestCase): 
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True 


    def test_index(self):
        result = self.app.get('/') 
        self.assertEqual(result.status_code, 200) 

if __name__ == '__main__':
    unittest2.main()

    