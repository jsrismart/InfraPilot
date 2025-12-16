export interface IaCResult {
  main?: string;
  variables?: string;
  outputs?: string;
  structure?: string[];
}

export interface PipelineResult {
  iac?: IaCResult;
  plan?: any;
  security?: any;
  finops?: any;
  [key: string]: any;
}
