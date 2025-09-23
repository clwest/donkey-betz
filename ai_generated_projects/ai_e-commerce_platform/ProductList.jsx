// React Native UI
import React from 'react';
import { View, Text, FlatList, TouchableOpacity } from 'react-native';

export const ProductList = ({ products, onProductSelect }) => {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>AI-Curated Products</Text>
            <FlatList
                data={products}
                keyExtractor={item => item.id}
                renderItem={({ item }) => (
                    <TouchableOpacity
                        style={styles.productCard}
                        onPress={() => onProductSelect(item)}
                    >
                        <Text style={styles.productName}>{item.name}</Text>
                        <Text style={styles.productPrice}>${item.price}</Text>
                    </TouchableOpacity>
                )}
            />
        </View>
    );
};
