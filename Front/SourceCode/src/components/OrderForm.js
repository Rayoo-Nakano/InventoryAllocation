import React, { useState } from 'react';
import { API } from 'aws-amplify';
import { Typography, TextField, Button, makeStyles } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  // スタイルの定義
}));

const OrderForm = () => {
  const classes = useStyles();
  const [itemCode, setItemCode] = useState('');
  const [quantity, setQuantity] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await API.post('api', '/orders', {
        body: {
          itemCode,
          quantity: parseInt(quantity),
        },
      });
      setItemCode('');
      setQuantity('');
    } catch (error) {
      console.error('Error creating order:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Typography variant="h4">受注登録</Typography>
      <TextField
        label="商品コード"
        value={itemCode}
        onChange={(e) => setItemCode(e.target.value)}
        required
      />
      <TextField
        label="数量"
        type="number"
        value={quantity}
        onChange={(e) => setQuantity(e.target.value)}
        required
      />
      <Button type="submit" variant="contained" color="primary">
        登録
      </Button>
    </form>
  );
};

export default OrderForm;