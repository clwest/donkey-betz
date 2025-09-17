import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// Import UI components to test
import { Button } from '../button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../card'
import { Badge } from '../badge'
import { Progress } from '../progress'
import { Alert, AlertDescription } from '../alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../tabs'
import { Checkbox } from '../checkbox'
import { Input } from '../input'

describe('UI Components', () => {
  const user = userEvent.setup()

  describe('Button Component', () => {
    it('renders button with text', () => {
      render(<Button>Click me</Button>)
      expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
    })

    it('handles click events', async () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick}>Click me</Button>)

      await user.click(screen.getByRole('button'))
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('supports different variants', () => {
      const { rerender } = render(<Button variant="destructive">Delete</Button>)
      expect(screen.getByRole('button')).toHaveClass('bg-destructive')

      rerender(<Button variant="outline">Cancel</Button>)
      expect(screen.getByRole('button')).toHaveClass('border-input')
    })

    it('supports different sizes', () => {
      const { rerender } = render(<Button size="sm">Small</Button>)
      expect(screen.getByRole('button')).toHaveClass('h-9')

      rerender(<Button size="lg">Large</Button>)
      expect(screen.getByRole('button')).toHaveClass('h-11')
    })

    it('can be disabled', () => {
      render(<Button disabled>Disabled</Button>)
      expect(screen.getByRole('button')).toBeDisabled()
    })

    it('supports loading state', () => {
      render(<Button disabled>Loading...</Button>)
      expect(screen.getByRole('button')).toBeDisabled()
    })
  })

  describe('Card Component', () => {
    it('renders card structure correctly', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
            <CardDescription>Card description</CardDescription>
          </CardHeader>
          <CardContent>Card content</CardContent>
        </Card>
      )

      expect(screen.getByText('Card Title')).toBeInTheDocument()
      expect(screen.getByText('Card description')).toBeInTheDocument()
      expect(screen.getByText('Card content')).toBeInTheDocument()
    })

    it('applies correct CSS classes', () => {
      render(
        <Card data-testid="card">
          <CardHeader data-testid="header">
            <CardTitle data-testid="title">Title</CardTitle>
          </CardHeader>
        </Card>
      )

      expect(screen.getByTestId('card')).toHaveClass('rounded-lg', 'border', 'bg-card')
      expect(screen.getByTestId('header')).toHaveClass('flex', 'flex-col', 'space-y-1.5', 'p-6')
      expect(screen.getByTestId('title')).toHaveClass('text-2xl', 'font-semibold')
    })
  })

  describe('Badge Component', () => {
    it('renders badge with text', () => {
      render(<Badge>New</Badge>)
      expect(screen.getByText('New')).toBeInTheDocument()
    })

    it('supports different variants', () => {
      const { rerender } = render(<Badge variant="destructive">Error</Badge>)
      expect(screen.getByText('Error')).toHaveClass('bg-destructive')

      rerender(<Badge variant="outline">Info</Badge>)
      expect(screen.getByText('Info')).toHaveClass('border')

      rerender(<Badge variant="secondary">Secondary</Badge>)
      expect(screen.getByText('Secondary')).toHaveClass('bg-secondary')
    })
  })

  describe('Progress Component', () => {
    it('renders progress bar', () => {
      render(<Progress value={50} />)
      const progressBar = screen.getByRole('progressbar')
      expect(progressBar).toBeInTheDocument()
      expect(progressBar).toHaveAttribute('aria-valuenow', '50')
    })

    it('displays correct percentage', () => {
      render(<Progress value={75} />)
      const progressBar = screen.getByRole('progressbar')
      expect(progressBar).toHaveAttribute('aria-valuenow', '75')
    })

    it('handles edge cases', () => {
      const { rerender } = render(<Progress value={0} />)
      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0')

      rerender(<Progress value={100} />)
      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '100')
    })
  })

  describe('Alert Component', () => {
    it('renders alert with description', () => {
      render(
        <Alert>
          <AlertDescription>This is an alert message</AlertDescription>
        </Alert>
      )

      expect(screen.getByText('This is an alert message')).toBeInTheDocument()
    })

    it('supports different variants', () => {
      const { rerender } = render(
        <Alert variant="destructive" data-testid="alert">
          <AlertDescription>Error message</AlertDescription>
        </Alert>
      )
      expect(screen.getByTestId('alert')).toHaveClass('border-destructive/50')

      rerender(
        <Alert variant="default" data-testid="alert">
          <AlertDescription>Default message</AlertDescription>
        </Alert>
      )
      expect(screen.getByTestId('alert')).toHaveClass('border-border')
    })
  })

  describe('Tabs Component', () => {
    it('renders tabs correctly', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      )

      expect(screen.getByRole('tab', { name: 'Tab 1' })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: 'Tab 2' })).toBeInTheDocument()
      expect(screen.getByText('Content 1')).toBeInTheDocument()
    })

    it('switches between tabs', async () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      )

      expect(screen.getByText('Content 1')).toBeInTheDocument()
      expect(screen.queryByText('Content 2')).not.toBeInTheDocument()

      await user.click(screen.getByRole('tab', { name: 'Tab 2' }))

      expect(screen.queryByText('Content 1')).not.toBeInTheDocument()
      expect(screen.getByText('Content 2')).toBeInTheDocument()
    })
  })

  describe('Checkbox Component', () => {
    it('renders checkbox', () => {
      render(<Checkbox />)
      expect(screen.getByRole('checkbox')).toBeInTheDocument()
    })

    it('handles check/uncheck', async () => {
      const handleChange = vi.fn()
      render(<Checkbox onCheckedChange={handleChange} />)

      const checkbox = screen.getByRole('checkbox')
      await user.click(checkbox)

      expect(handleChange).toHaveBeenCalledWith(true)
    })

    it('can be controlled', () => {
      const { rerender } = render(<Checkbox checked={false} />)
      expect(screen.getByRole('checkbox')).not.toBeChecked()

      rerender(<Checkbox checked={true} />)
      expect(screen.getByRole('checkbox')).toBeChecked()
    })
  })

  describe('Input Component', () => {
    it('renders input field', () => {
      render(<Input placeholder="Enter text" />)
      expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument()
    })

    it('handles input changes', async () => {
      const handleChange = vi.fn()
      render(<Input onChange={handleChange} />)

      const input = screen.getByRole('textbox')
      await user.type(input, 'Hello World')

      expect(input).toHaveValue('Hello World')
      expect(handleChange).toHaveBeenCalled()
    })

    it('supports different types', () => {
      const { rerender } = render(<Input type="password" />)
      expect(screen.getByDisplayValue('')).toHaveAttribute('type', 'password')

      rerender(<Input type="email" />)
      expect(screen.getByDisplayValue('')).toHaveAttribute('type', 'email')
    })

    it('can be disabled', () => {
      render(<Input disabled />)
      expect(screen.getByRole('textbox')).toBeDisabled()
    })
  })

  describe('Accessibility', () => {
    it('all interactive elements are keyboard accessible', async () => {
      render(
        <div>
          <Button>Button</Button>
          <Checkbox />
          <Input />
          <Tabs defaultValue="tab1">
            <TabsList>
              <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            </TabsList>
            <TabsContent value="tab1">Content</TabsContent>
          </Tabs>
        </div>
      )

      // Tab through all interactive elements
      await user.tab()
      expect(screen.getByRole('button')).toHaveFocus()

      await user.tab()
      expect(screen.getByRole('checkbox')).toHaveFocus()

      await user.tab()
      expect(screen.getByRole('textbox')).toHaveFocus()

      await user.tab()
      expect(screen.getByRole('tab')).toHaveFocus()
    })

    it('components have proper ARIA attributes', () => {
      render(
        <div>
          <Progress value={50} />
          <Alert>
            <AlertDescription>Alert</AlertDescription>
          </Alert>
          <Tabs defaultValue="tab1">
            <TabsList>
              <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            </TabsList>
            <TabsContent value="tab1">Content</TabsContent>
          </Tabs>
        </div>
      )

      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow')
      expect(screen.getByRole('tablist')).toBeInTheDocument()
      expect(screen.getByRole('tab')).toHaveAttribute('aria-selected')
    })
  })

  describe('Performance', () => {
    it('components render without performance issues', () => {
      const startTime = performance.now()

      render(
        <div>
          {Array.from({ length: 100 }, (_, i) => (
            <Card key={i}>
              <CardHeader>
                <CardTitle>Card {i}</CardTitle>
              </CardHeader>
              <CardContent>
                <Button>Button {i}</Button>
                <Badge>Badge {i}</Badge>
                <Progress value={i} />
              </CardContent>
            </Card>
          ))}
        </div>
      )

      const endTime = performance.now()
      expect(endTime - startTime).toBeLessThan(1000) // Should render in less than 1 second
    })
  })
})