export type Message = {
  id: string;
  from: string;
  to: string;
  sent: number;
  message: string;
  flagged: boolean;
};
