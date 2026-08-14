// Dashboard data types

export const ALL = "ALL";

export interface KpiData {
  totalAumCr: number;
  sipInflowCr: number;
  foliosCr: number;
  schemes: number;
}

export interface AumTrend {
  period: string;
  value: number;
}

export interface AmcAum {
  amc: string;
  aumCr: number;
}

export interface FundRow {
  amfiCode: string;
  schemeName: string;
  fundHouse: string;
  category: string;
  plan: string;
  navDate: string;
  nav: number;
  aum: number;
  sharpeRatio?: number;
  stdDev?: number;
  riskRating?: string;
  returnPercentage?: number;
}

export interface NavSeries {
  date: string;
  nav: number;
  benchmark?: number;
}

export interface StateTransaction {
  state: string;
  value: number;
}

export interface TransactionSplit {
  name: string;
  value: number;
}

export interface AgeGroupSip {
  ageGroup: string;
  avgSip: number;
}

export interface MonthlyVolume {
  month: string;
  volume: number;
}

export interface SipVsMarket {
  month: string;
  sip: number;
  nifty: number;
}

export interface CategoryInflow {
  category: string;
  [key: string]: number | string;
}

export interface FundCategory {
  name: string;
  count?: number;
}

export interface FundHouse {
  name: string;
  aum?: number;
  count?: number;
}

export interface FundPlan {
  name: string;
  count?: number;
}
