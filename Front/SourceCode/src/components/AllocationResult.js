import React, { useEffect, useState } from 'react';
import { API } from 'aws-amplify';
import { Typography, Table, TableHead, TableBody, TableRow, TableCell, makeStyles } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  // スタイルの定義
}));

const AllocationResult = () => {
  const classes = useStyles();
  const [allocations, setAllocations] = useState([]);

  useEffect(() => {
    fetchAllocations();
  }, []);

  const fetchAllocations = async () => {
    try {
      const allocationsData = await API.get('api', '/allocation-results');
      setAllocations(allocationsData);
    } catch (error) {
      console.error('Error fetching allocations:', error);
    }
  };

  return (
    <div>
      <Typography variant="h4">引当結果</Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>受注番号</TableCell>
            <TableCell>商品コード</TableCell>
            <TableCell>引当数量</TableCell>
            <TableCell>引当日</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {allocations.map((allocation) => (
            <TableRow key={allocation.id}>
              <TableCell>{allocation.orderId}</TableCell>
              <TableCell>{allocation.itemCode}</TableCell>
              <TableCell>{allocation.allocatedQuantity}</TableCell>
              <TableCell>{allocation.allocationDate}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default AllocationResult;