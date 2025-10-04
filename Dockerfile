FROM public.ecr.aws/lambda/python:3.12

# Install fonts for proper Unicode/Spanish character support
RUN microdnf install -y dejavu-sans-fonts dejavu-serif-fonts fontconfig && \
    microdnf clean all

# Copy requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Set the CMD to your handler
CMD ["app.lambda_handler"]