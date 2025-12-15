FROM public.ecr.aws/lambda/python:3.12

# Install dependencies from requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target ${LAMBDA_TASK_ROOT}

# Copy application code
COPY backend/ ${LAMBDA_TASK_ROOT}/backend/

# Set the handler (will be overridden by SST)
CMD ["backend/lambda_api.handler"]
