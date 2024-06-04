import React from 'react';
import { Amplify } from 'aws-amplify';
import { withAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import awsExports from './aws-exports';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import OrderForm from './components/OrderForm';
import InventoryForm from './components/InventoryForm';
import AllocationForm from './components/AllocationForm';
import AllocationResult from './components/AllocationResult';

Amplify.configure(awsExports);

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={Login} />
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/orders" component={OrderForm} />
        <Route path="/inventories" component={InventoryForm} />
        <Route path="/allocations" component={AllocationForm} />
        <Route path="/allocation-results" component={AllocationResult} />
      </Switch>
    </Router>
  );
}

export default withAuthenticator(App);
