FROM python:3.11-slim

#directorio de trabajo
WORKDIR /app

COPY . .

#dependencias
RUN pip install --no-cache-dir -r requirements.txt

#exponemos el puerto 8000 - para hacerlo accesible
EXPOSE 8000

#comando de ejecución
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]