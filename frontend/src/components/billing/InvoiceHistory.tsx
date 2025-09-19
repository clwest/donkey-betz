import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Receipt,
  Download,
  Eye,
  MoreVertical,
  Calendar,
  DollarSign,
  FileText
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface Invoice {
  id: number;
  invoice_number: string;
  total_amount: number;
  currency?: string;
  status: string;
  created_at: string;
  due_date?: string;
  period_start?: string;
  period_end?: string;
  line_items?: Array<{
    description: string;
    amount: number;
    quantity: number;
  }>;
}

interface Props {
  invoices: Invoice[];
}

const InvoiceHistory: React.FC<Props> = ({ invoices }) => {
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      paid: { variant: 'default' as const, text: 'Paid' },
      open: { variant: 'secondary' as const, text: 'Open' },
      draft: { variant: 'outline' as const, text: 'Draft' },
      void: { variant: 'destructive' as const, text: 'Void' },
      uncollectible: { variant: 'destructive' as const, text: 'Uncollectible' }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.open;
    return <Badge variant={config.variant}>{config.text}</Badge>;
  };

  const handleDownloadInvoice = async (invoiceId: number) => {
    try {
      // In a real implementation, this would download the PDF from the API
      toast.success('Invoice download functionality would be implemented here');
    } catch (error) {
      toast.error('Failed to download invoice');
    }
  };

  const handleViewDetails = (invoice: Invoice) => {
    setSelectedInvoice(invoice);
    setDetailDialogOpen(true);
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };

  const calculateTotalRevenue = () => {
    return invoices
      .filter(invoice => invoice.status === 'paid')
      .reduce((total, invoice) => total + invoice.total_amount, 0);
  };

  if (invoices.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Receipt className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Invoices</h3>
          <p className="text-muted-foreground">
            Your invoice history will appear here once you have a subscription
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Invoice History</h2>
          <p className="text-muted-foreground">
            View and download your billing history
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-right">
          <div>
            <p className="text-sm text-muted-foreground">Total Invoices</p>
            <p className="text-xl font-bold">{invoices.length}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Total Paid</p>
            <p className="text-xl font-bold text-green-600">
              {formatCurrency(calculateTotalRevenue())}
            </p>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            All Invoices
          </CardTitle>
          <CardDescription>
            Complete history of your billing and payments
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice #</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Period</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoices.map((invoice) => (
                  <TableRow key={invoice.id}>
                    <TableCell className="font-medium">
                      {invoice.invoice_number}
                    </TableCell>
                    <TableCell>
                      {new Date(invoice.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="font-semibold">
                      {formatCurrency(invoice.total_amount, invoice.currency)}
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(invoice.status)}
                    </TableCell>
                    <TableCell>
                      {invoice.period_start && invoice.period_end ? (
                        <span className="text-sm text-muted-foreground">
                          {new Date(invoice.period_start).toLocaleDateString()} - {' '}
                          {new Date(invoice.period_end).toLocaleDateString()}
                        </span>
                      ) : (
                        'N/A'
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleViewDetails(invoice)}>
                            <Eye className="h-4 w-4 mr-2" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={() => handleDownloadInvoice(invoice.id)}
                            disabled={invoice.status !== 'paid'}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Download PDF
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Invoice Detail Dialog */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Receipt className="h-5 w-5" />
              Invoice Details
            </DialogTitle>
            <DialogDescription>
              {selectedInvoice?.invoice_number}
            </DialogDescription>
          </DialogHeader>
          
          {selectedInvoice && (
            <div className="space-y-6">
              {/* Invoice Header */}
              <div className="grid grid-cols-2 gap-6 p-4 bg-muted/5 dark:bg-card rounded-lg">
                <div>
                  <h4 className="font-semibold mb-2">Invoice Information</h4>
                  <div className="space-y-1 text-sm">
                    <p><span className="font-medium">Number:</span> {selectedInvoice.invoice_number}</p>
                    <p><span className="font-medium">Date:</span> {new Date(selectedInvoice.created_at).toLocaleDateString()}</p>
                    <p><span className="font-medium">Status:</span> {getStatusBadge(selectedInvoice.status)}</p>
                    {selectedInvoice.due_date && (
                      <p><span className="font-medium">Due Date:</span> {new Date(selectedInvoice.due_date).toLocaleDateString()}</p>
                    )}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Billing Period</h4>
                  <div className="space-y-1 text-sm">
                    {selectedInvoice.period_start && selectedInvoice.period_end ? (
                      <>
                        <p><span className="font-medium">From:</span> {new Date(selectedInvoice.period_start).toLocaleDateString()}</p>
                        <p><span className="font-medium">To:</span> {new Date(selectedInvoice.period_end).toLocaleDateString()}</p>
                      </>
                    ) : (
                      <p className="text-muted-foreground">No billing period specified</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Line Items */}
              {selectedInvoice.line_items && selectedInvoice.line_items.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3">Invoice Items</h4>
                  <div className="border rounded-lg">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Description</TableHead>
                          <TableHead className="text-right">Quantity</TableHead>
                          <TableHead className="text-right">Amount</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {selectedInvoice.line_items.map((item, index) => (
                          <TableRow key={index}>
                            <TableCell>{item.description}</TableCell>
                            <TableCell className="text-right">{item.quantity}</TableCell>
                            <TableCell className="text-right font-medium">
                              {formatCurrency(item.amount, selectedInvoice.currency)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )}

              {/* Total */}
              <div className="border-t pt-4">
                <div className="flex justify-between items-center text-lg font-bold">
                  <span>Total Amount</span>
                  <span className="text-blue-600">
                    {formatCurrency(selectedInvoice.total_amount, selectedInvoice.currency)}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2 pt-4">
                <Button 
                  variant="outline" 
                  onClick={() => setDetailDialogOpen(false)}
                >
                  Close
                </Button>
                <Button 
                  onClick={() => handleDownloadInvoice(selectedInvoice.id)}
                  disabled={selectedInvoice.status !== 'paid'}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default InvoiceHistory;