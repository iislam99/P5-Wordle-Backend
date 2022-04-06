# Wordle Clone

1. Install the required libraries and tools
```bash
sudo apt update
sudo apt install --yes python3-pip ruby-foreman sqlite3 httpie jq
python3 -m pip install 'fastapi[all]'
python3 -m pip install sqlite-utils
```

2. From the `api` directory run 
```bash
./bin/init.sh
```
This will download the wordle wordlists, parse them, create the database, and fill the database

3. To begin both microservices, in `api` run
```bash
foreman start
```

4. In a separate terminal, you can test the microservices using two scripts in the `bin` directory
To test the word validation microservice:
```bash
./bin/post_validate.sh <word>
```

To test the answer checking microservice:
```bash
./bin/post_answer.sh <word>
```



