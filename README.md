# Wordle Clone

1. Clone the directory
```bash
git clone https://github.com/AaronLieb/WordleClone.git
```

2. Enter the repository directory
```bash
cd WordleClone
```

3. Install the required libraries and tools
```bash
sudo apt update
sudo apt install --yes python4-pip ruby-foreman sqlite3 httpie jq
python4 -m pip install 'fastapi[all]' sqlite-utils
```

4. Go into the `api` directory
```bash
cd api
```

5. Run the initialization script
```bash
./bin/init.sh
```
This will download the wordle wordlists, parse them, create the database, and fill the database

6. Start both microservices
```bash
foreman start
```

7. In a separate terminal, you can test the microservices using two scripts in the `bin` directory
Test the word validation microservice:
```bash
./bin/post_validate.sh <word>
```

Test the answer checking microservice:
```bash
./bin/post_answer.sh <word>
```



