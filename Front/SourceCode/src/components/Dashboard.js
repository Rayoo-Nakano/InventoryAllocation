import React, { useEffect, useState } from 'react';
import { API } from 'aws-amplify';
import { Typography, Grid, Paper, makeStyles } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  // スタイルの定義
}));

const Dashboard = () => {
  const classes = useStyles();
  const [orders, setOrders] = useState([]);
  const [inventories, setInventories] = useState([]);
  const [allocations, setAllocations] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const ordersData = await API.get('api', '/orders');
      const inventoriesData = await API.get('api', '/inventories');
      const allocationsData = await API.get('api', '/allocation-results');
      setOrders(ordersData);
      setInventories(inventoriesData);
      setAllocations(allocationsData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4">ダッシュボード</Typography>
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper>
          <Typography variant="h6">受注データ</Typography>
          {/* 受注データの表示 */}
        </Paper>
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper>
          <Typography variant="h6">在庫データ</Typography>
          {/* 在庫データの表示 */}
        </Paper>
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper>
          <Typography variant="h6">引当結果</Typography>
          {/* 引当結果の表示 */}
        </Paper>
      </Grid>
    </Grid>
  );
};

export default Dashboard;