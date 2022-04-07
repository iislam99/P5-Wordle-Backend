# Wordle Clone

1. Install the required libraries and tools
```bash
sudo apt update
sudo apt install --yes python3-pip ruby-foreman sqlite3 httpie jq
python3 -m pip install 'fastapi[all]' sqlite-utils
```

2. Go into the `api` directory

3. Run the initialization script
```bash
./bin/init.sh
```
This will download the wordle wordlists, parse them, create the database, and fill the database

4. Start both microservices
```bash
foreman start
```

5. In a separate terminal, you can test the microservices using two scripts in the `bin` directory
Test the word validation microservice:
```bash
./bin/post_validate.sh <word>
```

Test the answer checking microservice:
```bash
./bin/post_answer.sh <word>
```



