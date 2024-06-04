import React, { useState } from 'react';
import { API } from 'aws-amplify';
import { Typography, TextField, Button, makeStyles } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  // スタイルの定義
}));

const InventoryForm = () => {
  const classes = useStyles();
  const [itemCode, setItemCode] = useState('');
  const [quantity, setQuantity] = useState('');
  const [receiptDate, setReceiptDate] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await API.post('api', '/inventories', {
        body: {
          itemCode,
          quantity: parseInt(quantity),
          receiptDate,
        },
      });
      setItemCode('');
      setQuantity('');
      setReceiptDate('');
    } catch (error) {
      console.error('Error creating inventory:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Typography variant="h4">在庫登録</Typography>
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
      <TextField
        label="入荷日"
        type="date"
        value={receiptDate}
        onChange={(e) => setReceiptDate(e.target.value)}
        required
      />
      <Button type="submit" variant="contained" color="primary">
        登録
      </Button>
    </form>
  );
};

export default InventoryForm;