import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProductList = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');

    useEffect(() => {
        fetchProducts();
    }, []);

    const fetchProducts = async () => {
        try {
            const response = await axios.get('/api/products/');
            setProducts(response.data);
        } catch (error) {
            console.error('Error fetching products:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredProducts = products.filter(product =>
        product.name.toLowerCase().includes(filter.toLowerCase())
    );

    if (loading) return <div>Loading...</div>;

    return (
        <div className="product-list">
            <input
                type="text"
                placeholder="Search products..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
            />
            <div className="products-grid">
                {filteredProducts.map(product => (
                    <ProductCard key={product.id} product={product} />
                ))}
            </div>
        </div>
    );
};

const ProductCard = ({ product }) => (
    <div className="product-card">
        <h3>{product.name}</h3>
        <p>{product.description}</p>
        <span className="price">${product.price}</span>
        <button onClick={() => addToCart(product.id)}>Add to Cart</button>
    </div>
);

export default ProductList;
