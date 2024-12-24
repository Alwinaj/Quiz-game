# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404

from .models import Category, Question, Answer

def home(request):
    categories = Category.objects.all()
    return render(request, 'quiz/home.html', {'categories': categories})

def quiz(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    questions = category.questions.all()

    # Initialize session variables if not already set
    if 'current_question' not in request.session:
        request.session['current_question'] = 0
        request.session['score'] = 0
        request.session['answers'] = [None] * questions.count()

    current_question_index = request.session['current_question']
    current_question = questions[current_question_index]

    if request.method == "POST":
        selected_answer = request.POST.get('answer')
        if selected_answer:
            request.session['answers'][current_question_index] = selected_answer
            request.session.modified = True

        if 'next' in request.POST:
            request.session['current_question'] += 1
        elif 'previous' in request.POST and current_question_index > 0:
            request.session['current_question'] -= 1

        if request.session['current_question'] >= questions.count():
            # Calculate the score
            score = 0
            for i, question in enumerate(questions):
                selected_answer = request.session['answers'][i]
                if selected_answer is not None:
                    try:
                        selected_answer_obj = Answer.objects.get(id=int(selected_answer))
                        if selected_answer_obj.is_correct:
                            score += 1
                    except Answer.DoesNotExist:
                        continue

            # Save the score in session
            request.session['score'] = score
            return redirect('result', category_id=category_id)

    return render(request, 'quiz/quiz.html', {
        'category': category,
        'question': current_question,
        'question_index': current_question_index + 1,
        'total_questions': questions.count()
    })

def result(request, category_id):
    score = request.session.get('score', 0)
    total_questions = Category.objects.get(id=category_id).questions.count()

    # Clear session data
    request.session.flush()
    return render(request, 'quiz/result.html', {'score': score, 'total_questions': total_questions})
