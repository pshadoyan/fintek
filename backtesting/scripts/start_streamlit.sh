#!/bin/bash

# Find the Streamlit executable
STREAMLIT_EXEC=$(which streamlit)

# Run Streamlit if it's found
if [ -n "$STREAMLIT_EXEC" ]; then
    # Set the host to 0.0.0.0 and specify the port
    exec $STREAMLIT_EXEC run streamlit_app.py --server.address=0.0.0.0 --server.port=8501
else
    echo "Streamlit executable not found"
    exit 1
fi
