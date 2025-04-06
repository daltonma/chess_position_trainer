FROM cs50/server

# Install Stockfish, PIP dependencies
RUN apt-get update && apt-get install -y Stockfish

RUN pip3 install --no-cache-dir \
    chess \
    stockfish

# Remove the default server files
RUN rm -rf /var/www/

WORKDIR /var/www/
# Copy the source code into the container
RUN git clone https://github.com/bohrium2b/chess_position_trainer

WORKDIR /var/www/chess_position_trainer

EXPOSE 8080
CMD passenger start 