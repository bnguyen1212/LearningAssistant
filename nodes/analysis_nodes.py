from typing import Dict, List
from datetime import datetime

from graph.state import ConversationState, Message
from services.llm_service import LLMService

class AnalysisNodes:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def analyze_conversation_topics(self, state: ConversationState) -> ConversationState:
        """
        Analyze the full conversation to identify distinct topics for note generation
        """
        print("🔍 Analyzing conversation for topics...")
        
        # Convert full conversation to format expected by LLM service
        conversation_dict = []
        for msg in state["full_conversation"]:
            conversation_dict.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Analyze topics using LLM
        try:
            topics = self.llm_service.analyze_conversation_topics(conversation_dict)
            
            if topics:
                print(f"📋 Identified {len(topics)} topics:")
                for i, topic in enumerate(topics, 1):
                    print(f"   {i}. {topic}")
                
                state["identified_topics"] = topics
            else:
                print("❌ No topics identified")
                state["identified_topics"] = []
                
        except Exception as e:
            print(f"❌ Error analyzing topics: {e}")
            state["identified_topics"] = []
        
        return state
    
    def generate_notes_for_topics(self, state: ConversationState) -> ConversationState:
        """
        Generate structured notes for each identified topic
        """
        print("📝 Generating notes for identified topics...")
        
        topics = state["identified_topics"]
        if not topics:
            print("⚠️ No topics to generate notes for")
            state["generated_notes"] = {}
            return state
        
        # Convert full conversation to format expected by LLM service
        conversation_dict = []
        for msg in state["full_conversation"]:
            conversation_dict.append({
                "role": msg.role,
                "content": msg.content
            })
        
        generated_notes = {}
        
        for topic in topics:
            print(f"✍️ Generating note for: {topic}")
            
            try:
                note_content = self.llm_service.generate_note_for_topic(
                    topic=topic,
                    full_conversation=conversation_dict
                )
                
                if note_content:
                    generated_notes[topic] = note_content
                    print(f"✅ Generated note for: {topic} ({len(note_content)} chars)")
                else:
                    print(f"❌ Failed to generate note for: {topic}")
                    
            except Exception as e:
                print(f"❌ Error generating note for {topic}: {e}")
                continue
        
        state["generated_notes"] = generated_notes
        
        if generated_notes:
            print(f"📚 Successfully generated {len(generated_notes)} notes")
        else:
            print("⚠️ No notes were generated")
        
        return state
    
    def validate_generated_content(self, state: ConversationState) -> ConversationState:
        """
        Validate that we have content to save and provide summary
        """
        topics = state["identified_topics"]
        notes = state["generated_notes"]
        
        print("\n" + "=" * 50)
        print("📊 CONTENT GENERATION SUMMARY")
        print("=" * 50)
        
        if not topics:
            print("❌ No topics identified from conversation")
            return state
        
        if not notes:
            print("❌ No notes generated")
            return state
        
        print(f"✅ Topics identified: {len(topics)}")
        print(f"✅ Notes generated: {len(notes)}")
        
        # Show preview of generated content
        print("\n📋 Generated content preview:")
        for topic, content in notes.items():
            print(f"\n🔹 {topic}")
            print(f"   Content length: {len(content)} characters")
            print(f"   Preview: {content[:100]}...")
        
        print("\n" + "=" * 50)
        print("✅ Content validation complete - ready to save!")
        
        return state
    
    def check_analysis_complete(self, state: ConversationState) -> str:
        """
        Conditional edge: check if analysis and generation is complete
        """
        if state["generated_notes"]:
            return "save_notes"
        else:
            return "analysis_failed"
    
    def handle_analysis_failure(self, state: ConversationState) -> ConversationState:
        """
        Handle case where topic analysis or note generation failed
        """
        print("❌ Analysis or note generation failed")
        print("💬 Continuing conversation without saving notes")
        
        # Reset note-related state
        state["note_request_detected"] = False
        state["identified_topics"] = []
        state["generated_notes"] = {}
        
        return state