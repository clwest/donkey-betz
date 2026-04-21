// React Component
import React from 'react';

export const ProductList = ({ products }) => {
    return (
        <div>
            {products.map(p => <div key={p.id}>{p.name}</div>)}
        </div>
    );
};
