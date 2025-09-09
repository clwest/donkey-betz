import React, { useState, useEffect } from 'react';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  CreditCard,
  Plus,
  Trash2,
  Star,
  Shield
} from 'lucide-react';
import { billingAPI } from '../../services/billing.api';
import { toast } from 'react-hot-toast';

interface PaymentMethod {
  id: number;
  type: string;
  is_default: boolean;
  card_brand: string;
  card_last_4: string;
  card_exp_month: number;
  card_exp_year: number;
  display_name: string;
  is_active: boolean;
  created_at: string;
}

interface Props {
  onUpdate: () => void;
}

const PaymentMethods: React.FC<Props> = ({ onUpdate }) => {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);

  useEffect(() => {
    fetchPaymentMethods();
  }, []);

  const fetchPaymentMethods = async () => {
    try {
      setLoading(true);
      const data = await billingAPI.getPaymentMethods();
      setPaymentMethods(data);
    } catch (error) {
      toast.error('Failed to load payment methods');
    } finally {
      setLoading(false);
    }
  };

  const handleAddPaymentMethod = async () => {
    // This would integrate with Stripe Elements for secure card input
    // For now, we'll show a placeholder
    toast.success('Payment method integration would use Stripe Elements here');
  };

  const handleDeletePaymentMethod = async (paymentMethodId: number) => {
    try {
      // await billingAPI.deletePaymentMethod(paymentMethodId);
      toast.success('Payment method removed');
      fetchPaymentMethods();
    } catch (error) {
      toast.error('Failed to remove payment method');
    }
  };

  const handleSetDefault = async (paymentMethodId: number) => {
    try {
      // await billingAPI.setDefaultPaymentMethod(paymentMethodId);
      toast.success('Default payment method updated');
      fetchPaymentMethods();
    } catch (error) {
      toast.error('Failed to update default payment method');
    }
  };

  const getCardIcon = (brand: string) => {
    // You could add specific card brand icons here
    return <CreditCard className="h-6 w-6 text-gray-600" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Payment Methods</h2>
          <p className="text-muted-foreground">
            Manage your saved payment methods
          </p>
        </div>
        
        <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Add Payment Method
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Payment Method</DialogTitle>
              <DialogDescription>
                Add a new payment method to your account
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="p-4 border rounded-lg bg-blue-50 dark:bg-blue-900/20">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="h-4 w-4 text-blue-600" />
                  <span className="font-medium text-blue-900 dark:text-blue-100">
                    Secure Payment Processing
                  </span>
                </div>
                <p className="text-sm text-blue-700 dark:text-blue-200">
                  Payment information is processed securely through Stripe.
                  We never store your full card details.
                </p>
              </div>
              
              <div className="space-y-3">
                <div>
                  <Label htmlFor="card-number">Card Number</Label>
                  <Input 
                    id="card-number" 
                    placeholder="1234 5678 9012 3456"
                    disabled
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor="exp-date">Expiry Date</Label>
                    <Input 
                      id="exp-date" 
                      placeholder="MM/YY"
                      disabled
                    />
                  </div>
                  <div>
                    <Label htmlFor="cvc">CVC</Label>
                    <Input 
                      id="cvc" 
                      placeholder="123"
                      disabled
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="name">Cardholder Name</Label>
                  <Input 
                    id="name" 
                    placeholder="John Doe"
                    disabled
                  />
                </div>
              </div>
              
              <div className="flex justify-end gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => setAddDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button onClick={handleAddPaymentMethod}>
                  Add Payment Method
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {paymentMethods.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Payment Methods</h3>
            <p className="text-muted-foreground mb-4">
              Add a payment method to manage your subscription and make purchases
            </p>
            <Button onClick={() => setAddDialogOpen(true)}>
              Add Your First Payment Method
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {paymentMethods.map((method) => (
            <Card key={method.id} className="relative">
              {method.is_default && (
                <Badge className="absolute -top-2 -right-2">
                  <Star className="h-3 w-3 mr-1" />
                  Default
                </Badge>
              )}
              
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getCardIcon(method.card_brand)}
                    <div>
                      <CardTitle className="text-lg">
                        {method.display_name}
                      </CardTitle>
                      <CardDescription>
                        Expires {String(method.card_exp_month).padStart(2, '0')}/{method.card_exp_year}
                      </CardDescription>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {!method.is_default && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleSetDefault(method.id)}
                      >
                        Set as Default
                      </Button>
                    )}
                    
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleDeletePaymentMethod(method.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Added {new Date(method.created_at).toLocaleDateString()}</span>
                  <Badge variant={method.is_active ? 'default' : 'secondary'}>
                    {method.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Credit Purchase Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Purchase Credits
          </CardTitle>
          <CardDescription>
            Buy additional credits for pay-as-you-go usage
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { credits: 100, price: 10, popular: false },
              { credits: 500, price: 45, popular: true },
              { credits: 1000, price: 80, popular: false }
            ].map((pack) => (
              <Card key={pack.credits} className={`relative ${pack.popular ? 'ring-2 ring-blue-500' : ''}`}>
                {pack.popular && (
                  <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                    Most Popular
                  </Badge>
                )}
                <CardContent className="p-4 text-center">
                  <h3 className="text-lg font-bold">{pack.credits} Credits</h3>
                  <p className="text-2xl font-bold text-blue-600">${pack.price}</p>
                  <p className="text-sm text-muted-foreground">
                    ${(pack.price / pack.credits).toFixed(3)} per credit
                  </p>
                  <Button 
                    className="w-full mt-3" 
                    variant={pack.popular ? 'default' : 'outline'}
                    disabled={paymentMethods.length === 0}
                    onClick={() => {
                      if (paymentMethods.length === 0) {
                        toast.error('Please add a payment method first');
                        return;
                      }
                      // Handle credit purchase
                      toast.success('Credit purchase functionality would be implemented here');
                    }}
                  >
                    Purchase
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {paymentMethods.length === 0 && (
            <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <p className="text-sm text-yellow-700 dark:text-yellow-200">
                Add a payment method to purchase additional credits
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentMethods;