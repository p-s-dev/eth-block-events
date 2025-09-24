# Ethereum Block Events

A Spring Boot Java application that uses RxJava events to listen to an Infura node with Web3j. When blockchain events happen, it publishes them to a Google Guava EventBus for easy consumption by other components.

## Features

- **Spring Boot Integration**: Easy configuration and dependency injection
- **Web3j Integration**: Connect to Ethereum nodes (Infura, local nodes, etc.)
- **RxJava Reactive Streams**: Efficient event handling using reactive programming
- **Google Guava EventBus**: Publish/Subscribe pattern for event distribution
- **Configurable Event Filtering**: Listen to specific contract events based on Solidity event signatures
- **ERC20 Support**: Built-in support for ERC20 Transfer events with automatic decoding
- **Extensible Architecture**: Easy to add new event types and handlers

## Configuration

### Application Properties

Configure your Ethereum connection and contracts in `application.yml`:

```yaml
ethereum:
  # Your Infura project URL (or any other Ethereum node)
  node-url: https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID
  
  # Starting block number (null means start from latest)
  start-block: null
  
  # Block polling interval in milliseconds
  block-polling-interval: 1000
  
  # Contract configurations
  contracts:
    # Example ERC20 token contract (USDC)
    - name: "USDC"
      address: "0xA0b86a33E6441c8c6c0D4B7D5E7b4F5B7E7E7E7E"
      events:
        - name: "Transfer"
          signature: "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
          topics: []
          enabled: true
```

### Environment-Specific Configuration

- `application.yml` - Default configuration
- `application-dev.yml` - Development configuration (testnet)
- `application-test.yml` - Test configuration

## Usage

### Running the Application

```bash
# Build the application
mvn clean package

# Run with default profile
java -jar target/eth-block-events-1.0.0-SNAPSHOT.jar

# Run with development profile (testnet)
java -jar target/eth-block-events-1.0.0-SNAPSHOT.jar --spring.profiles.active=dev
```

### Maven Commands

```bash
# Compile the project
mvn compile

# Run tests
mvn test

# Package the application
mvn package

# Run the application directly
mvn spring-boot:run
```

### Docker Usage

#### Option 1: Using Multi-stage Dockerfile (Recommended)

Build and run in one step:

```bash
# Build the Docker image
docker build -t eth-block-events .

# Run the container
docker run --rm eth-block-events

# Run with custom profile
docker run --rm -e SPRING_PROFILES_ACTIVE=dev eth-block-events

# Run with environment variables
docker run --rm \
  -e SPRING_PROFILES_ACTIVE=dev \
  -e ETHEREUM_NODE_URL=https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID \
  eth-block-events
```

#### Option 2: Using Separate Build and Runtime Dockerfiles

Build the application:

```bash
# Build using the build Dockerfile
docker build -f Dockerfile.build -t eth-block-events:build .

# Extract the built JAR
docker create --name temp-container eth-block-events:build
docker cp temp-container:/app/target/eth-block-events-1.0.0-SNAPSHOT.jar .
docker rm temp-container

# Build the runtime image
docker build -f Dockerfile.run -t eth-block-events:run .

# Run the application
docker run --rm eth-block-events:run
```

#### Option 3: Using Docker Compose

```bash
# Run with Docker Compose
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

#### Docker Environment Variables

You can configure the application using environment variables:

- `SPRING_PROFILES_ACTIVE` - Set the active Spring profile (dev, prod, test)
- `ETHEREUM_NODE_URL` - Override the Ethereum node URL
- `ETHEREUM_START_BLOCK` - Set the starting block number
- `ETHEREUM_BLOCK_POLLING_INTERVAL` - Set the polling interval in milliseconds

Example:

```bash
docker run --rm \
  -e SPRING_PROFILES_ACTIVE=dev \
  -e ETHEREUM_NODE_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID \
  -e ETHEREUM_START_BLOCK=18000000 \
  -e ETHEREUM_BLOCK_POLLING_INTERVAL=2000 \
  eth-block-events
```

## Event Handling

### Listening to Events

The application automatically publishes events to the EventBus. Create a service to handle them:

```java
@Service
public class MyEventHandler {
    
    @PostConstruct
    public void initialize() {
        eventBus.register(this);
    }
    
    @Subscribe
    public void handleEthereumEvent(EthereumEvent event) {
        // Handle generic Ethereum events
        logger.info("Received event: {} from contract: {}", 
                   event.eventName(), event.contractAddress());
    }
    
    @Subscribe
    public void handleERC20Transfer(ERC20TransferEvent event) {
        // Handle ERC20 Transfer events specifically
        logger.info("ERC20 Transfer: {} tokens from {} to {}", 
                   event.value(), event.from(), event.to());
    }
}
```

### Event Types

#### EthereumEvent
Generic event containing:
- Event name
- Contract address
- Transaction hash
- Block number and timestamp
- Raw topics and data

#### ERC20TransferEvent
Specific event for ERC20 transfers containing:
- From/To addresses
- Transfer amount
- Contract address
- Transaction details

## Adding New Event Types

1. **Create Event Model**:
```java
public record MyCustomEvent(
    String contractAddress,
    String customData,
    // ... other fields
) {
    public static final String EVENT_SIGNATURE = "MyEvent(address,string)";
}
```

2. **Configure in application.yml**:
```yaml
contracts:
  - name: "MyContract"
    address: "0x..."
    events:
      - name: "MyEvent"
        signature: "0x..." # Event signature hash
        enabled: true
```

3. **Add Handler Logic** in `EthereumEventListenerService`:
```java
if ("MyEvent".equals(eventConfig.name())) {
    handleMyCustomEvent(log);
}
```

## Common Event Signatures

| Event | Signature | Hash |
|-------|-----------|------|
| ERC20 Transfer | `Transfer(address,address,uint256)` | `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` |
| ERC20 Approval | `Approval(address,address,uint256)` | `0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925` |
| ERC721 Transfer | `Transfer(address,address,uint256)` | `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` |

## Requirements

- Java 17+
- Maven 3.6+
- Infura account (or access to an Ethereum node)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Ethereum      │    │   Application    │    │   Event         │
│   Node/Infura   │◄──►│   (Web3j +      │◄──►│   Handlers      │
│                 │    │    RxJava)       │    │   (EventBus)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

The application:
1. Connects to Ethereum nodes via Web3j
2. Sets up RxJava subscriptions for configured contract events
3. Processes incoming events and publishes them to EventBus
4. Event handlers consume events via the @Subscribe annotation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.