Here is an example of a simple shopping cart frontend interface using React with hooks, state management, and API integration:

```jsx
import React, { useState, useEffect } from 'react';

const ShoppingCart = () => {
  const [items, setItems] = useState([]);
  const [totalPrice, setTotalPrice] = useState(0);

  useEffect(() => {
    fetch('https://api.example.com/cart')
      .then(response => response.json())
      .then(data => {
        setItems(data.items);
        setTotalPrice(data.totalPrice);
      });
  }, []);

  const handleRemoveItem = (itemId) => {
    const updatedItems = items.filter(item => item.id !== itemId);
    const updatedTotalPrice = updatedItems.reduce((acc, item) => acc + item.price, 0);
    setItems(updatedItems);
    setTotalPrice(updatedTotalPrice);
  };

  return (
    <div>
      <h2>Shopping Cart</h2>
      <ul>
        {items.map(item => (
          <li key={item.id}>
            <span>{item.name} - ${item.price}</span>
            <button onClick={() => handleRemoveItem(item.id)}>Remove</button>
          </li>
        ))}
      </ul>
      <p>Total Price: ${totalPrice}</p>
    </div>
  );
};

export default ShoppingCart;
```

In this example, the component fetches cart data from an API when it mounts using `useEffect`. The fetched data includes items in the shopping cart and the total price. The component then renders the list of items with a "Remove" button that calls the `handleRemoveItem` function to remove an item from the cart and update the total price accordingly.