# TiDB Serverless Setup Guide - Day 1 Critical Path

## Immediate Action Required

To proceed with Day 1 execution, we need TiDB Serverless connection configured.

## Option 1: Quick Setup (Recommended for Hackathon)

### Step 1: Create TiDB Serverless Account
1. Go to https://tidbcloud.com/
2. Sign up for free account
3. Create a new Serverless cluster
4. Note the connection details

### Step 2: Get Connection String
The connection string format is:
```
mysql+pymysql://[username].[cluster-id]:[password]@gateway01.[region].prod.aws.tidbcloud.com:4000/[database]?ssl_verify_cert=true&ssl_verify_identity=true
```

### Step 3: Set Environment Variable
```bash
export TIDB_CONNECTION_STRING="mysql+pymysql://your_username.your_cluster:your_password@gateway01.us-west-2.prod.aws.tidbcloud.com:4000/test?ssl_verify_cert=true&ssl_verify_identity=true"
```

## Option 2: Local Development (Fallback)

If TiDB Serverless setup is blocked, we can use local MySQL for development:

### Install MySQL locally
```bash
brew install mysql
brew services start mysql
```

### Create local database
```bash
mysql -u root -e "CREATE DATABASE beast_mode_hackathon;"
```

### Set local connection string
```bash
export TIDB_CONNECTION_STRING="mysql+pymysql://root@localhost:3306/beast_mode_hackathon"
```

## Option 3: SQLite Fallback (Emergency)

For immediate development, we can use SQLite:

```bash
export TIDB_CONNECTION_STRING="sqlite:///beast_mode_hackathon.db"
```

## Validation

After setting up connection, run:
```bash
python3 tidb_integration_day1.py
```

Should see:
```
✅ TiDB connection successful
✅ Beast Mode schema created successfully
✅ Message stored: test-message-001
✅ Retrieved 1 messages
✅ Agent Stats: {...}
🎉 Day 1 TiDB Integration: SUCCESS!
```

## Next Steps After Connection Success

1. ✅ TiDB connected and storing messages
2. ✅ Basic analytics working  
3. ✅ Ready for Day 2: Full Beast Mode integration

## Emergency Contact

If blocked on TiDB setup:
- TiDB Community: https://discord.gg/tidb
- Documentation: https://docs.pingcap.com/tidbcloud/
- Support: https://support.pingcap.com/

**Time is critical - we need this working TODAY for hackathon success!**