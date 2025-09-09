import React from 'react';
import { View, Text, Platform, StyleSheet, TouchableOpacity } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import { theme } from '../styles/theme';
import * as Haptics from 'expo-haptics';

// Import screens
import HomeScreen from '../screens/HomeScreen';
import StudioScreen from '../screens/StudioScreen';
import GalleryScreen from '../screens/GalleryScreen';
import AssistantScreen from '../screens/AssistantScreen';
import ProfileScreen from '../screens/ProfileScreen';
import MoreScreen from '../screens/MoreScreen';

// Import screens that will be in More menu
import CharacterScreen from '../screens/CharacterScreen';
import CampaignScreen from '../screens/CampaignScreen';
import OddsCalculatorScreen from '../../app/odds/index';
import ConnectivityMonitorScreen from '../../app/connectivity/index';
import NCAAfBoardScreen from '../../app/sports/board';
import SportsBettingScreen from '../../app/sports/SportsBoardScreen';
import PersonalAssistantTest from '../tests/PersonalAssistantTest';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Stack navigator for More section
function MoreStackNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyleInterpolator: ({ current, layouts }) => {
          return {
            cardStyle: {
              transform: [
                {
                  translateX: current.progress.interpolate({
                    inputRange: [0, 1],
                    outputRange: [layouts.screen.width, 0],
                  }),
                },
              ],
              opacity: current.progress.interpolate({
                inputRange: [0, 1],
                outputRange: [0, 1],
              }),
            },
          };
        },
      }}
    >
      <Stack.Screen name="MoreMenu" component={MoreScreen} />
      <Stack.Screen name="Characters" component={CharacterScreen} />
      <Stack.Screen name="Campaigns" component={CampaignScreen} />
      <Stack.Screen name="OddsCalculator" component={OddsCalculatorScreen} />
      <Stack.Screen name="ConnectivityMonitor" component={ConnectivityMonitorScreen} />
      <Stack.Screen name="NCAAfBoard" component={NCAAfBoardScreen} />
      <Stack.Screen name="SportsBetting" component={SportsBettingScreen} />
      <Stack.Screen name="PersonalAssistantTest" component={PersonalAssistantTest} />
    </Stack.Navigator>
  );
}

// Custom tab bar component for that premium feel
const CustomTabBar = ({ state, descriptors, navigation }: any) => {
  return (
    <View style={styles.tabBarContainer}>
      <BlurView intensity={80} tint="dark" style={styles.blurView}>
        <View style={styles.tabBar}>
          {state.routes.map((route: any, index: number) => {
            const { options } = descriptors[route.key];
            const label = options.tabBarLabel ?? options.title ?? route.name;
            const isFocused = state.index === index;

            const onPress = () => {
              const event = navigation.emit({
                type: 'tabPress',
                target: route.key,
                canPreventDefault: true,
              });

              if (!isFocused && !event.defaultPrevented) {
                if (Platform.OS !== 'web') {
                  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                }
                navigation.navigate(route.name);
              }
            };

            const icon = getTabIcon(route.name, isFocused);

            return (
              <View key={index} style={styles.tabItem}>
                <TouchableOpacity
                  onPress={onPress}
                  style={styles.tabButton}
                  activeOpacity={0.7}
                >
                  {isFocused && (
                    <LinearGradient
                      colors={theme.colors.primary.gradient}
                      style={styles.activeTabGradient}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 1 }}
                    />
                  )}
                  <Text style={styles.tabIcon}>{icon}</Text>
                  <Text
                    style={[
                      styles.tabLabel,
                      isFocused ? styles.tabLabelActive : styles.tabLabelInactive,
                    ]}
                  >
                    {label}
                  </Text>
                </TouchableOpacity>
              </View>
            );
          })}
        </View>
      </BlurView>
    </View>
  );
};

const getTabIcon = (routeName: string, isFocused: boolean) => {
  switch (routeName) {
    case 'Home':
      return '🏠';
    case 'Studio':
      return '✨';
    case 'Gallery':
      return '📚';
    case 'Assistant':
      return '🤖';
    case 'More':
      return '⋯';
    case 'Profile':
      return '👤';
    default:
      return '📱';
  }
};

export default function TabNavigator() {
  return (
    <Tab.Navigator
      tabBar={(props) => <CustomTabBar {...props} />}
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ tabBarLabel: 'Home' }}
      />
      <Tab.Screen 
        name="Studio" 
        component={StudioScreen}
        options={{ tabBarLabel: 'Studio' }}
      />
      <Tab.Screen 
        name="Gallery" 
        component={GalleryScreen}
        options={{ tabBarLabel: 'Library' }}
      />
      <Tab.Screen 
        name="Assistant" 
        component={AssistantScreen}
        options={{ tabBarLabel: 'Assistant' }}
      />
      <Tab.Screen 
        name="More" 
        component={MoreStackNavigator}
        options={{ tabBarLabel: 'More' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ tabBarLabel: 'Profile' }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  tabBarContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: Platform.OS === 'ios' ? 90 : 70,
  },
  blurView: {
    flex: 1,
    backgroundColor: Platform.OS === 'android' ? theme.colors.background.secondary : 'transparent',
  },
  tabBar: {
    flexDirection: 'row',
    height: '100%',
    paddingBottom: Platform.OS === 'ios' ? 20 : 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.secondary,
  },
  tabItem: {
    flex: 1,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  activeTabGradient: {
    position: 'absolute',
    width: 48,
    height: 48,
    borderRadius: 24,
    opacity: 0.2,
  },
  tabIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  tabLabel: {
    fontSize: 11,
    fontWeight: '600',
  },
  tabLabelActive: {
    color: theme.colors.primary.main,
  },
  tabLabelInactive: {
    color: theme.colors.text.tertiary,
  },
});