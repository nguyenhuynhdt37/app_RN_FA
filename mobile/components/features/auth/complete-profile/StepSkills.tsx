import React from 'react'
import { View, Pressable, ActivityIndicator } from 'react-native'
import { Text } from '../../../ui/Text';
import { MotiView } from 'moti';
import * as Haptics from 'expo-haptics';
import { useTranslation } from 'react-i18next';
import { BadgeCheck } from 'lucide-react-native';
import { useQuery } from '@tanstack/react-query';
import { metaService } from '../../../../src/services/meta.service';

interface UserSpecialization {
  name: string
  level: string
  skills: string[]
}

interface StepSkillsProps {
  specializations: any[]
  setSpecializations: (v: any[]) => void
  selectedInterestIds: string[]
  setSelectedInterestIds: (l: string[]) => void
}

export function StepSkills({
  specializations, setSpecializations, selectedInterestIds = [], setSelectedInterestIds
}: StepSkillsProps) {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language === 'vi' ? 'vi' : 'en';

  const { data: remoteSpecs, isLoading: specsLoading } = useQuery({
    queryKey: ['specializations'],
    queryFn: metaService.getSpecializations
  });

  const { data: remoteInterests, isLoading: interestsLoading } = useQuery({
    queryKey: ['interests'],
    queryFn: metaService.getInterests
  });

  const toggleSkill = (specId: string, skillId: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSpecializations(prev => prev.map(s => {
      if (s.specialization_id === specId) {
        const skillIds = s.skill_ids || [];
        return {
          ...s,
          skill_ids: skillIds.includes(skillId) 
            ? skillIds.filter(i => i !== skillId) 
            : [...skillIds, skillId]
        };
      }
      return s;
    }));
  };

  const toggleInterest = (id: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSelectedInterestIds(prev => {
      const currentList = prev || [];
      if (currentList.includes(id)) {
        return currentList.filter(i => i !== id);
      } else {
        return [...currentList, id];
      }
    });
  };

  if (specsLoading || interestsLoading) {
    return (
      <View className="h-40 items-center justify-center">
        <ActivityIndicator color="#10b981" />
      </View>
    );
  }

  return (
    <MotiView
      from={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ type: 'timing', duration: 400 }}
    >
      {specializations.map((spec) => {
        // Find the remote spec to get its skills and name
        const remoteSpec = remoteSpecs?.find(rs => rs.id === spec.specialization_id);
        const specName = currentLang === 'vi' ? remoteSpec?.name_vi : remoteSpec?.name_en;
        
        const availableSkills = remoteSpec?.skills || [];

        return (
          <View key={spec.specialization_id} className="mb-8">
            <View className="flex-row items-center gap-2 mb-4">
              <View className="w-1.5 h-6 bg-emerald-500 rounded-full" />
              <Text className="text-zinc-900 dark:text-zinc-50 font-extrabold text-lg uppercase tracking-wider">
                {specName} <Text className="text-emerald-500 font-medium">({t(`auth.profile.education.levels.${spec.level}`)})</Text>
              </Text>
            </View>
            
            <View className="flex-row flex-wrap gap-2">
              {availableSkills.map(skill => {
                const skillName = currentLang === 'vi' ? skill.name_vi : skill.name_en;
                const isSelected = spec.skill_ids.includes(skill.id);
                return (
                  <Pressable 
                    key={skill.id}
                    onPress={() => toggleSkill(spec.specialization_id, skill.id)}
                    className={`px-4 py-2.5 rounded-2xl border ${
                      isSelected 
                        ? 'bg-emerald-500/20 border-emerald-500' 
                        : 'bg-white/30 dark:bg-zinc-900/70 border-zinc-300 dark:border-zinc-700'
                    }`}
                  >
                    <View className="flex-row items-center gap-2">
                      <Text className={`font-bold ${isSelected ? 'text-emerald-700 dark:text-emerald-400' : 'text-zinc-800 dark:text-zinc-200'}`}>
                        {skillName}
                      </Text>
                      {isSelected && <BadgeCheck size={16} color="#059669" />}
                    </View>
                  </Pressable>
                );
              })}
            </View>
          </View>
        );
      })}

      <View className="mt-4 pt-6 border-t border-zinc-200 dark:border-zinc-800">
        <Text className="text-zinc-900 dark:text-zinc-50 font-bold mb-4 ml-1 uppercase tracking-widest text-xs color-zinc-500">
          {t('auth.profile.skills.interests_label')}
        </Text>
        <View className="flex-row flex-wrap gap-2">
          {remoteInterests?.map(interest => {
            const interestName = currentLang === 'vi' ? interest.name_vi : interest.name_en;
            const isSelected = selectedInterestIds.includes(interest.id);
            return (
              <Pressable 
                key={interest.id}
                onPress={() => toggleInterest(interest.id)}
                className={`px-5 py-3 rounded-full border ${
                  isSelected 
                    ? 'bg-zinc-900 dark:bg-zinc-100 border-zinc-900 dark:border-zinc-100' 
                    : 'bg-white/10 dark:bg-zinc-900/50 border-zinc-200 dark:border-zinc-800'
                }`}
              >
                <Text className={`font-bold ${isSelected ? 'text-white dark:text-zinc-900' : 'text-zinc-500 dark:text-zinc-400'}`}>
                  {interestName}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </View>
    </MotiView>
  )
}
