# Token Purchase and Resale Flow Analysis

## Overview

This system operates as a cryptocurrency-powered marketplace where users can deposit various cryptocurrencies, convert them to platform credits, purchase items, and withdraw funds. The flow involves multiple stages from initial deposit to final withdrawal/resale.

## 1. Token Deposit Flow

### Supported Cryptocurrencies
- **Bitcoin (BTC)** - Native Bitcoin network
- **Litecoin (LTC)** - Native Litecoin network  
- **Solana (SOL)** - Solana network
- **USDT TRC20** - Tether on TRON network
- **USDT ERC20** - Tether on Ethereum network
- **USDC ERC20** - USD Coin on Ethereum network

### Deposit Process

1. **Payment Request Creation** (`services/payment.py`)
   - User selects cryptocurrency type
   - System creates payment request via KryptoExpress API
   - Generates unique deposit address for user
   - Returns address, expected crypto amount, and fiat equivalent

2. **Deposit Detection** (`crypto_api/CryptoApiManager.py`)
   - System continuously monitors blockchain networks for deposits
   - Each cryptocurrency has dedicated monitoring function:
     - `get_new_btc_deposits()` - Monitors Bitcoin mempool
     - `get_new_ltc_deposits()` - Monitors Litecoin via BlockCypher API
     - `get_sol_balance()` - Monitors Solana via Solana FM API
     - `get_usdt_trc20_balance()` - Monitors TRON network
     - `get_usdt_erc20_balance()` - Monitors Ethereum via Ethplorer
     - `get_usdc_erc20_balance()` - Monitors USDC on Ethereum

3. **Credit Assignment** (`processing/processing.py`)
   - Confirmed deposits are converted to platform credits
   - Credits added to user's `top_up_amount` field
   - System tracks conversion via `fiatAmount` from payment processing

## 2. Purchase Flow

### Cart Management (`services/cart.py`)

1. **Add to Cart**
   - Users browse categories and subcategories
   - Items added to cart with specified quantities
   - Cart persists across sessions

2. **Checkout Process**
   - System validates item availability
   - Calculates total cost including all items
   - Checks user's available balance: `(top_up_amount - consume_records) >= cart_total`

3. **Purchase Execution**
   - Creates `Buy` record with buyer info and total price
   - Creates `BuyItem` records linking specific items to purchase
   - Marks items as `is_sold = True`
   - Updates user's `consume_records` with purchase amount
   - Removes items from cart
   - Sends purchase notification

### Balance Management
- **Available Balance** = `top_up_amount - consume_records`
- **top_up_amount**: Total deposits converted to platform credits
- **consume_records**: Total amount spent on purchases

## 3. Item Management

### Purchase Recording (`models/buy.py`)
```python
class Buy:
    buyer_id: User ID
    quantity: Number of items purchased
    total_price: Total amount paid
    buy_datetime: Timestamp of purchase
    is_refunded: Refund status
```

### Item Tracking (`models/buyItem.py`)
- Links specific items to purchase records
- Enables item delivery and refund tracking
- Maintains purchase history

## 4. Resale/Withdrawal Flow

### Admin Withdrawal Management (`services/admin.py`)

1. **Withdrawal Request**
   - Admin initiates withdrawal via admin panel
   - Selects cryptocurrency type
   - Provides destination address
   - System validates address format using regex patterns

2. **Withdrawal Calculation** 
   - System calculates via KryptoExpress API:
     - Total withdrawal amount
     - Blockchain fees
     - Service fees  
     - Net receiving amount
   - Shows fiat equivalent at current exchange rates

3. **Withdrawal Execution** (`crypto_api/CryptoApiWrapper.py`)
   - Creates `WithdrawalDTO` with withdrawal details
   - Executes withdrawal via KryptoExpress API
   - Returns transaction IDs for blockchain verification
   - Provides links to blockchain explorers for each network

### Supported Withdrawal Networks
- **Bitcoin**: Bitcoin network explorer
- **Litecoin**: Litecoin Space explorer  
- **Solana**: Solscan explorer
- **Ethereum**: Etherscan explorer
- **BNB**: BSCscan explorer

## 5. Refund System (`services/buy.py`)

### Refund Process
1. Admin selects purchase for refund
2. System reverts user balance:
   - Reduces `consume_records` by refund amount
   - Marks purchase as `is_refunded = True`
3. Sends refund notification to user
4. Purchase items remain marked as sold (inventory not restored)

## 6. Key Integration Points

### External APIs
- **KryptoExpress API**: Payment processing and withdrawals
- **Blockchain APIs**: Deposit monitoring across networks
- **CoinGecko/Kraken**: Real-time cryptocurrency pricing

### Database Models
- **User**: Balance tracking (`top_up_amount`, `consume_records`)
- **Payment**: Deposit request tracking
- **Deposit**: Confirmed blockchain deposits
- **Buy/BuyItem**: Purchase records and item tracking
- **Cart/CartItem**: Shopping cart management

## 7. Security Features

1. **Address Validation**: Regex validation for all cryptocurrency addresses
2. **Balance Verification**: Prevents overspending via balance checks
3. **Confirmation Requirements**: Multiple confirmation steps for withdrawals
4. **Transaction Limits**: Maximum 5 pending payments per user
5. **Audit Trail**: Complete transaction history tracking

## Flow Summary

```
Crypto Deposit → Platform Credits → Item Purchase → Potential Withdrawal
     ↓                ↓                 ↓               ↓
[Blockchain]    [top_up_amount]   [consume_records]  [Crypto Resale]
```

The system effectively converts cryptocurrency deposits into platform purchasing power, tracks all transactions, and provides withdrawal capabilities for unused funds, creating a complete token economy within the marketplace.