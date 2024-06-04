import React, { useState } from 'react';
import { API } from 'aws-amplify';
import { Typography, FormControl, InputLabel, Select, MenuItem, Button, makeStyles } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  // スタイルの定義
}));

const AllocationForm = () => {
  const classes = useStyles();
  const [allocationMethod, setAllocationMethod] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await API.post('api', '/allocate', {
        body: {
          allocationMethod,
        },
      });
      setAllocationMethod('');
    } catch (error) {
      console.error('Error allocating inventory:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Typography variant="h4">在庫引当</Typography>
      <FormControl>
        <InputLabel>引当方法</InputLabel>
        <Select
          value={allocationMethod}
          onChange={(e) => setAllocationMethod(e.target.value)}
          required
        >
          <MenuItem value="FIFO">先入先出法（FIFO）</MenuItem>
          <MenuItem value="LIFO">後入先出法（LIFO）</MenuItem>
          {/* 他の引当方法のオプションを追加 */}
        </Select>
      </FormControl>
      <Button type="submit" variant="contained" color="primary">
        引当実行
      </Button>
    </form>
  );
};

export default AllocationForm;