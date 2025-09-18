// home page have profile, family name, food, other items, food gone off etc.

import React, { useEffect, useState } from "react";
import axios from "axios";
import FoodItemsPad from "./FoodItemsPad";
import OtherItemsPad from "./OtherItemsPad";
import Layout from "./Layout";


const HomePage = () => {
  return (
    <Layout>
      <h1 className="my-4">Welcome to Family Dashboard</h1>
      <FoodItemsPad />
      <OtherItemsPad />
    </Layout>
  );
};
export default HomePage;