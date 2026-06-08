# Netflix Dashboard Task 4

This Streamlit app allows users to upload a CSV dataset and explore the data with dynamic charts. It includes controls for chart type, x/y axes, color grouping, and filtering.

## Run the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The app accepts CSV uploads via the Streamlit file uploader.
- If `netflix_titles.csv` exists one directory above this folder, the app will use it automatically.
